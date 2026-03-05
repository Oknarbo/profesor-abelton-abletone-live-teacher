# Profesor Abelton Remote Script
# Compatible with Ableton Live 10, 11, and 12
# Author: Profesor Abelton Team
# Version: 2.0.2 - Live 12 FULL COMPATIBILITY
# Last Updated: 2025-11-09 22:00
# EMERGENCY FIX: Remove all deprecation warnings

import sys
import socket
import json
import threading
import time
import warnings

# Disable all deprecation warnings for Live 12 compatibility
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Correct import for Ableton 10/11/12
from _Framework.ControlSurface import ControlSurface  # pylint: disable=import-error
ABLETON_VERSION = "10+"

class AICopilotControlSurface(ControlSurface):
    """
    Main control surface for Profesor Abelton
    Provides bidirectional communication between Ableton and AI Server
    """
    
    def __init__(self, c_instance):
        super(AICopilotControlSurface, self).__init__(c_instance)
        self._c_instance = c_instance
        self.socket_client = None
        self.server_thread = None
        self.command_thread = None
        self.polling_thread = None  # Added missing polling_thread
        self.is_running = False
        self.last_state = {}
        self.server_host = 'localhost'
        self.server_port = 8766
        self.command_queue = []
        self.is_ableton_10_plus = True  # Assume modern Ableton version
        self.last_created_track_index = -1 # Track index of the last created track
        self.reconnect_attempts = 0  # New: Track reconnect attempts
        self.max_reconnect_attempts = 5  # New: Max attempts
        
        self.log_message("=" * 60)
        self.log_message("PROFESOR ABELTON REMOTE SCRIPT v2.0.0")
        self.log_message("=" * 60)
        self.log_message(f"Ableton Version: {ABLETON_VERSION}")
        self.log_message(f"Server: {self.server_host}:{self.server_port}")
        self.log_message("=" * 60)
        
        try:
            self.log_message("[1/3] Testing socket creation...")
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.log_message("[1/3] OK - Socket created")
        
            self.log_message(f"[2/3] Testing server connection...")
            test_sock.settimeout(2.0)
            test_sock.connect((self.server_host, self.server_port))
            self.log_message("[2/3] OK - Server reachable")
            test_sock.close()
        
        except Exception as e:
            self.log_message(f"[ERROR] Connection test failed: {str(e)}")
        
        self.log_message("[3/3] Starting monitoring threads...")
        try:
            self.connect_script()
            self.log_message("[3/3] OK - Threads started")
            self.log_message("=" * 60)
            self.log_message("PROFESOR ABELTON FULLY INITIALIZED!")
            self.log_message("=" * 60)
            # New: Add listener for song changes
            self.song().add_listener('tracks', self._on_song_changed)
            self.log_message("📡 Song change listener added")
        except Exception as e:
            self.log_message(f"[ERROR] connect_script() failed: {str(e)}")
            self.log_message(f"[ERROR] Exception type: {type(e).__name__}")
        
    def disconnect(self):
        """Called when the script is unloaded"""
        self.log_message("🛑 Profesor Abelton Shutting Down...")
        self.is_running = False
        if self.socket_client:
            try:
                self.socket_client.close()
            except:
                pass
        # New: Remove listener
        try:
            self.song().remove_listener('tracks', self._on_song_changed)
            self.log_message("📡 Song change listener removed")
        except:
            pass
        # New: Prepare for reconnect on next init
        self.reconnect_attempts = 0
        super(AICopilotControlSurface, self).disconnect()
        
    def log_message(self, msg):
        """Log messages to Ableton's log"""
        try:
            self._c_instance.log_message(str(msg))
        except Exception as e:
            self._c_instance.log_message(unicode(msg))  # Fallback for Live 12
        
    def connect_script(self):
        """Initialize connections and start background threads"""
        self.log_message("  -> connect_script() called")
        self.is_running = True
        
        # New: Reconnect logic
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(2.0)
                test_sock.connect((self.server_host, self.server_port))
                test_sock.close()
                self.log_message("✅ Server connection successful")
                break
            except Exception as e:
                self.reconnect_attempts += 1
                self.log_message(f"⚠️ Reconnect attempt {self.reconnect_attempts}/{self.max_reconnect_attempts} failed: {e}")
                time.sleep(1.0)
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.log_message("❌ Max reconnect attempts reached. Please restart server.")
            return
        
        try:
            # Start state monitoring thread
            self.log_message("  -> Creating state monitor thread...")
            self.server_thread = threading.Thread(target=self._state_monitor_loop)
            self.server_thread.daemon = True
            self.server_thread.start()
            self.log_message("  -> State monitor thread started")
            
            # Start persistent connection thread instead of polling
            self.log_message("  -> Creating persistent connection thread...")
            self.connection_thread = threading.Thread(target=self._persistent_connection_loop)
            self.connection_thread.daemon = True
            self.connection_thread.start()
            self.log_message("  -> Persistent connection thread started")
            
            # Start command execution thread
            self.log_message("  -> Creating command execution thread...")
            self.command_thread = threading.Thread(target=self._command_execution_loop)
            self.command_thread.daemon = True
            self.command_thread.start()
            self.log_message("  -> Command execution thread started")
            
            self.log_message("  -> connect_script() completed successfully")
        except Exception as e:
            self.log_message(f"  -> ERROR in connect_script(): {str(e)}")
        
    def _state_monitor_loop(self):
        """Background thread that monitors Ableton state and sends updates"""
        self.log_message("🔄 State monitor loop started")
        last_heartbeat_time = time.time()
        
        while self.is_running:
            try:
                state = self._capture_ableton_state()
                current_time = time.time()
                
                # Send update if state changed OR every 5 seconds (heartbeat)
                state_changed = state != self.last_state
                heartbeat_needed = (current_time - last_heartbeat_time) >= 5.0
                
                if state_changed or heartbeat_needed:
                    if state_changed:
                        self.log_message("📤 Sending state update (changed)...")
                    else:
                        self.log_message("💓 Sending heartbeat...")
                    
                    self._send_state_to_server(state)
                    self.last_state = state
                    last_heartbeat_time = current_time
                    self.log_message("✅ Update sent")
                    
                time.sleep(2.0)  # Increased to 2s
            except Exception as e:
                self.log_message(f"⚠️ State monitor error: {e}")
                time.sleep(2.0)
                
    def _persistent_connection_loop(self):
        """Maintain persistent connection to server for bidirectional communication"""
        self.log_message("🔄 Persistent connection loop started")
        while self.is_running:
            try:
                self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_client.settimeout(5.0)
                self.socket_client.connect((self.server_host, self.server_port))
                self.log_message("✅ Established persistent connection to server")
                
                # Send initial ping or identification
                self.socket_client.sendall(json.dumps({"type": "connect", "client": "ableton"}).encode('utf-8') + b'\n')
                
                # Now use this socket for sending states in _send_state_to_server
                # And read commands in a loop
                buffer = ""
                while self.is_running:
                    try:
                        data = self.socket_client.recv(8192).decode('utf-8')
                        if not data:
                            break
                        
                        buffer += data
                        # Process complete messages (split by \n delimiter)
                        while '\n' in buffer:
                            message_str, buffer = buffer.split('\n', 1)
                            if not message_str.strip():
                                continue  # Skip empty lines
                            try:
                                response = json.loads(message_str)
                                if response.get("type") == "commands":
                                    commands = response.get("commands", [])
                                    if commands:
                                        self.log_message(f"📥 Received {len(commands)} command(s) via persistent connection")
                                        for cmd in commands:
                                            self.command_queue.append(cmd)
                                elif response.get("type") == "mcp_tool_call":
                                    # Handle MCP tool call
                                    tool_name = response.get("tool_name")
                                    tool_input = response.get("tool_input", {})
                                    self.log_message(f"🔧 MCP Tool Call: {tool_name}")
                                    self.log_message(f"📝 Tool Input: {tool_input}")

                                    # Execute the tool
                                    try:
                                        result = self._execute_mcp_tool(tool_name, tool_input)

                                        # Send result back
                                        result_message = {
                                            "type": "mcp_tool_result",
                                            "tool_name": tool_name,
                                            "tool_call_id": response.get("tool_call_id"),
                                            "status": "success" if result.get("success") else "error",
                                            "result": result.get("result"),
                                            "error": result.get("error"),
                                            "timestamp": time.time()
                                        }
                                        self.socket_client.sendall(json.dumps(result_message).encode('utf-8') + b'\n')
                                        self.log_message(f"✅ MCP Tool Result Sent: {result.get('success', False)}")

                                    except Exception as e:
                                        error_message = {
                                            "type": "mcp_tool_result",
                                            "tool_name": tool_name,
                                            "status": "error",
                                            "error": str(e),
                                            "timestamp": time.time()
                                        }
                                        self.socket_client.sendall(json.dumps(error_message).encode('utf-8') + b'\n')
                                        self.log_message(f"❌ MCP Tool Error: {e}")
                            except json.JSONDecodeError as e:
                                self.log_message(f"⚠️ JSON parse error: {e}")
                    except socket.timeout:
                        continue
                    except Exception as e:
                        self.log_message(f"⚠️ Read error in persistent connection: {e}")
                        break
                
            except Exception as e:
                self.log_message(f"⚠️ Persistent connection error: {e}")
                if self.socket_client:
                    self.socket_client.close()
                    self.socket_client = None
                time.sleep(2.0)  # Wait before reconnect
            
    def _command_polling_loop(self):
        """Background thread that polls server for commands"""
        self.log_message("🔄 Command polling loop started")
        retry_attempts = 0
        max_retries = 3
        while self.is_running:
            try:
                # Ask server for pending commands
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect((self.server_host, self.server_port))
                
                message = {
                    "type": "get_commands",
                    "timestamp": time.time()
                }
                
                sock.sendall(json.dumps(message).encode('utf-8') + b'\n')
                
                # Receive response
                response_data = sock.recv(8192).decode('utf-8')
                # Handle newline delimiter
                if '\n' in response_data:
                    response_data = response_data.split('\n')[0]  # Take first message
                response = json.loads(response_data)
                sock.close()
 
                # Queue received commands for execution
                if response.get("status") == "ok":
                    commands = response.get("commands", [])
                    if commands:
                        self.log_message(f"📥 Received {len(commands)} command(s) from server:")
                        for i, cmd in enumerate(commands):
                            self.log_message(f"  {i+1}. {cmd.get('action', 'unknown')}")
                        for cmd in commands:
                            self.command_queue.append(cmd)
                    else:
                        # Only log when polling if there are no commands (reduce spam)
                        pass
                else:
                    self.log_message(f"⚠️ Server response error: {response}")
                
                retry_attempts = 0  # Reset retries on success
                time.sleep(2.0)  # Increased to 2s
                
            except Exception as e:
                retry_attempts += 1
                self.log_message(f"⚠️ Polling error (attempt {retry_attempts}/{max_retries}): {e}")
                if retry_attempts >= max_retries:
                    self.log_message("❌ Max polling retries reached. Pausing for 5s...")
                    time.sleep(5.0)
                    retry_attempts = 0
                else:
                    time.sleep(1.0)
                
    def _command_execution_loop(self):
        """Background thread that executes queued commands"""
        self.log_message("🔄 Command execution loop started")
        while self.is_running:
            try:
                if self.command_queue:
                    command = self.command_queue.pop(0)
                    self.log_message(f"🎯 Executing queued command: {command.get('action', 'unknown')}")
                    self._execute_command(command)
                    self.log_message(f"✅ Command executed: {command.get('action')}")
                    time.sleep(1)  # Add delay to prevent overload
                time.sleep(0.1)
            except Exception as e:
                self.log_message(f"⚠️ Command execution error: {e}")
                import traceback
                self.log_message(f"Traceback: {traceback.format_exc()}")
                
    def _capture_ableton_state(self):
        """Capture current state of Ableton Live session"""
        try:
            song = self.song()
            state = {
                "tempo": float(song.tempo),
                "is_playing": bool(song.is_playing),
                "loop_enabled": bool(song.loop),
                "record_mode": bool(song.record_mode),
                "metronome": bool(song.metronome),
                "tracks": []
            }
            
            # Capture track information
            for idx, track in enumerate(song.tracks):
                track_info = {
                    "index": idx,
                    "name": str(track.name),
                    "type": "audio" if track.has_audio_input else "midi",
                    "muted": bool(track.mute),
                    "solo": bool(track.solo),
                    "armed": bool(track.arm) if track.can_be_armed else False,
                    "volume": float(track.mixer_device.volume.value) if hasattr(track, 'mixer_device') else 1.0,
                    "devices": [],
                    "clips": []
                }
                
                # Capture devices
                try:
                    for device in track.devices:
                        track_info["devices"].append({
                            "name": str(device.name),
                            "type": str(device.class_name),
                            "is_active": bool(device.is_active)
                        })
                except:
                    pass
                
                # Capture clips
                try:
                    for slot_idx, clip_slot in enumerate(track.clip_slots):
                        if clip_slot.has_clip:
                            clip = clip_slot.clip
                            clip_info = {
                                "slot": slot_idx,
                                "name": str(clip.name),
                                "length": float(clip.length),
                                "is_playing": bool(clip.is_playing),
                                "is_recording": bool(clip.is_recording) if hasattr(clip, 'is_recording') else False
                            }
                            track_info["clips"].append(clip_info)
                except:
                    pass
                    
                state["tracks"].append(track_info)
            
            return state
            
        except Exception as e:
            self.log_message(f"⚠️ Error capturing state: {e}")
            return {}
            
    def _send_state_to_server(self, state):
        """Send current state to AI server using persistent socket if available"""
        retry_attempts = 0
        max_retries = 3
        while retry_attempts < max_retries:
            try:
                if not self.socket_client:
                    raise Exception("No persistent connection")
                    
                message = {
                    "type": "state_update",
                    "data": state,
                    "timestamp": time.time()
                }
 
                self.socket_client.sendall(json.dumps(message).encode('utf-8') + b'\n')  # Add delimiter
                self.log_message("📨 State data sent via persistent connection")
                return  # Success
 
            except Exception as e:
                retry_attempts += 1
                self.log_message(f"❌ Failed to send state (attempt {retry_attempts}): {e}")
                if retry_attempts < max_retries:
                    time.sleep(1.0)
                else:
                    self.log_message(f"❌ Max retries reached. Will retry on next cycle.")
                    pass
                
    def receive_command_from_server(self, command_data):
        """Receive and queue command from AI server"""
        try:
            self.command_queue.append(command_data)
            self.log_message(f"📥 Command queued: {command_data.get('action', 'unknown')}")
        except Exception as e:
            self.log_message(f"⚠️ Error queuing command: {e}")
            
    def _execute_command(self, command):
        """Execute a command in Ableton"""
        try:
            action = command.get('action')
            self.log_message(f"⚡ Executing: {action}")

            if action == 'create_audio_track':
                result = self._create_track('audio', command)
                self.log_message(f"✅ create_audio_track completed, result: {result}")
            elif action == 'create_midi_track':
                result = self._create_track('midi', command)
                self.log_message(f"✅ create_midi_track completed, result: {result}")
            elif action == 'set_tempo':
                self._set_tempo(command)
                self.log_message(f"✅ set_tempo completed")
            elif action == 'play':
                self._transport_play()
                self.log_message(f"✅ play completed")
            elif action == 'stop':
                self._transport_stop()
                self.log_message(f"✅ stop completed")
            elif action == 'record':
                self._transport_record(command)
                self.log_message(f"✅ record completed")
            elif action == 'add_device':
                self._add_device(command)
                self.log_message(f"✅ add_device completed")
            elif action == 'set_track_volume':
                self._set_track_volume(command)
                self.log_message(f"✅ set_track_volume completed")
            elif action == 'set_track_pan':
                self._set_track_pan(command)
                self.log_message(f"✅ set_track_pan completed")
            elif action == 'mute_track':
                self._mute_track(command)
                self.log_message(f"✅ mute_track completed")
            elif action == 'solo_track':
                self._solo_track(command)
                self.log_message(f"✅ solo_track completed")
            elif action == 'arm_track':
                self._arm_track(command)
                self.log_message(f"✅ arm_track completed")
            elif action == 'create_clip':
                self._create_clip(command)
                self.log_message(f"✅ create_clip completed")
            elif action == 'add_notes':
                self._add_notes(command)
                self.log_message(f"✅ add_notes completed")
            elif action == 'delete_track':
                self._delete_track(command)
                self.log_message(f"✅ delete_track completed")
            elif action == 'play_clip':
                self._play_clip(command)
                self.log_message(f"✅ play_clip completed")
            elif action == 'stop_clip':
                self._stop_clip(command)
                self.log_message(f"✅ stop_clip completed")
            elif action == 'group_tracks':
                self._group_tracks(command)
                self.log_message(f"✅ group_tracks completed")
            elif action == 'ungroup_tracks':
                self._ungroup_tracks(command)
                self.log_message(f"✅ ungroup_tracks completed")
            # === TRACK MANAGEMENT EXTENSIONS ===
            elif action == 'add_return_track':
                self._add_return_track(command)
                self.log_message(f"✅ add_return_track completed")
            elif action == 'rename_track':
                self._rename_track(command)
                self.log_message(f"✅ rename_track completed")
            elif action == 'set_track_color':
                self._set_track_color(command)
                self.log_message(f"✅ set_track_color completed")
            elif action == 'duplicate_track':
                self._duplicate_track(command)
                self.log_message(f"✅ duplicate_track completed")
            elif action == 'move_track':
                self._move_track(command)
                self.log_message(f"✅ move_track completed")
            # === MIDI EXTENSIONS ===
            elif action == 'add_single_note':
                self._add_single_note(command)
                self.log_message(f"✅ add_single_note completed")
            elif action == 'delete_notes':
                self._delete_notes(command)
                self.log_message(f"✅ delete_notes completed")
            elif action == 'transpose_notes':
                self._transpose_notes(command)
                self.log_message(f"✅ transpose_notes completed")
            elif action == 'humanize_notes':
                self._humanize_notes(command)
                self.log_message(f"✅ humanize_notes completed")
            elif action == 'quantize_notes':
                self._quantize_notes(command)
                self.log_message(f"✅ quantize_notes completed")
            elif action == 'create_drum_pattern':
                self._create_drum_pattern(command)
                self.log_message(f"✅ create_drum_pattern completed")
            # === DEVICE EXTENSIONS ===
            elif action == 'remove_device':
                self._remove_device(command)
                self.log_message(f"✅ remove_device completed")
            elif action == 'toggle_device':
                self._toggle_device(command)
                self.log_message(f"✅ toggle_device completed")
            elif action == 'set_device_parameter':
                self._set_device_parameter(command)
                self.log_message(f"✅ set_device_parameter completed")
            elif action == 'set_send_level':
                self._set_send_level(command)
                self.log_message(f"✅ set_send_level completed")
            elif action == 'load_device_preset':
                self._load_device_preset(command)
                self.log_message(f"✅ load_device_preset completed")
            # === BONUS FEATURES ===
            elif action == 'record_audio':
                self._record_audio(command)
                self.log_message(f"✅ record_audio completed")
            elif action == 'export_audio':
                self._export_audio(command)
                self.log_message(f"✅ export_audio completed")
            elif action == 'undo_action':
                self._undo_action(command)
                self.log_message(f"✅ undo_action completed")
            elif action == 'save_snapshot':
                self._save_snapshot(command)
                self.log_message(f"✅ save_snapshot completed")
            elif action == 'set_loop_markers':
                self._set_loop_markers(command)
                self.log_message(f"✅ set_loop_markers completed")
            elif action == 'consolidate_clip':
                self._consolidate_clip(command)
                self.log_message(f"✅ consolidate_clip completed")
            else:
                self.log_message(f"⚠️ Unknown command: {action}")

        except Exception as e:
            self.log_message(f"❌ Command execution failed: {e} - Possible timeout")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}")
            # Don't re-raise exception to prevent Ableton from crashing
            
    def _create_track(self, track_type, command):
        """Create a new track"""
        song = self.song()
        position = command.get('position', command.get('index', -1))

        track_count_before = len(song.tracks)
        self.log_message(f"📊 Tracks before creation: {track_count_before}")

        if track_type == 'audio':
            song.create_audio_track(position)
        else:
            song.create_midi_track(position)

        track_count_after = len(song.tracks)
        track_index = track_count_after - 1
        self.last_created_track_index = track_index  # Update global last index
        self.log_message(f"✅ Created {track_type} track at index {track_index} (total tracks: {track_count_after})")
        return track_index
        
    def _set_tempo(self, command):
        """Set song tempo"""
        song = self.song()
        bpm = float(command.get('bpm', 120))
        song.tempo = max(20, min(999, bpm))  # Clamp between valid range
        self.log_message(f"✅ Tempo set to {bpm} BPM")
        
    def _transport_play(self):
        """Start playback"""
        self.song().start_playing()
        self.log_message("▶️ Playback started")
        
    def _transport_stop(self):
        """Stop playback"""
        self.song().stop_playing()
        self.log_message("⏹️ Playback stopped")
        
    def _transport_record(self, command):
        """Toggle recording"""
        song = self.song()
        song.record_mode = not song.record_mode
        self.log_message(f"🔴 Recording: {song.record_mode}")
        
    def _add_device(self, command):
        """Add device/effect to track"""
        try:
            track_idx = command.get('track_index', 0)
            device_name = command.get('device_name', '').lower()
            device_type = command.get('device_type', 'instrument')  # instrument, audio_effect, midi_effect
            
            song = self.song()
            
            if track_idx >= len(song.tracks):
                self.log_message(f"⚠️ Track {track_idx} does not exist")
                return
            
            track = song.tracks[track_idx]
            
            # Try to use browser to load device
            try:
                browser = self.application().browser
                
                # Enhanced device mappings with more options
                device_mappings = {
                    # Instruments
                    'kick': ('Drums', 'Kicks'),
                    'drum rack': ('Drums', 'Drum Rack'),
                    'simpler': ('Instruments', 'Simpler'),
                    'sampler': ('Instruments', 'Sampler'),
                    'operator': ('Instruments', 'Operator'),
                    'analog': ('Instruments', 'Analog'),
                    'collision': ('Instruments', 'Collision'),
                    'electric': ('Instruments', 'Electric'),
                    'tension': ('Instruments', 'Tension'),
                    'wavetable': ('Instruments', 'Wavetable'),
                    'impulse': ('Instruments', 'Impulse'),
                    
                    # Audio Effects (expanded)
                    'reverb': ('Audio Effects', 'Reverb'),
                    'delay': ('Audio Effects', 'Simple Delay'),
                    'echo': ('Audio Effects', 'Echo'),
                    'eq eight': ('Audio Effects', 'EQ Eight'),
                    'eq three': ('Audio Effects', 'EQ Three'),
                    'compressor': ('Audio Effects', 'Compressor'),
                    'glue compressor': ('Audio Effects', 'Glue Compressor'),
                    'limiter': ('Audio Effects', 'Limiter'),
                    'saturator': ('Audio Effects', 'Saturator'),
                    'chorus': ('Audio Effects', 'Chorus'),
                    'flanger': ('Audio Effects', 'Flanger'),
                    'phaser': ('Audio Effects', 'Phaser'),
                    'auto filter': ('Audio Effects', 'Auto Filter'),
                    'auto pan': ('Audio Effects', 'Auto Pan'),
                    'erosion': ('Audio Effects', 'Erosion'),
                    'redux': ('Audio Effects', 'Redux'),
                    'vinyl distortion': ('Audio Effects', 'Vinyl Distortion'),
                    'gate': ('Audio Effects', 'Gate'),
                    'filter delay': ('Audio Effects', 'Filter Delay'),
                    'frequency shifter': ('Audio Effects', 'Frequency Shifter'),
                    'spectrum': ('Audio Effects', 'Spectrum'),
                    'vocoder': ('Audio Effects', 'Vocoder'),
                    
                    # MIDI Effects
                    'arpeggiator': ('MIDI Effects', 'Arpeggiator'),
                    'chord': ('MIDI Effects', 'Chord'),
                    'note length': ('MIDI Effects', 'Note Length'),
                    'pitch': ('MIDI Effects', 'Pitch'),
                    'random': ('MIDI Effects', 'Random'),
                    'scale': ('MIDI Effects', 'Scale'),
                    'velocity': ('MIDI Effects', 'Velocity'),
                }
                
                matched_category = None
                matched_device = None
                
                for key, (category, device) in device_mappings.items():
                    if key in device_name or device_name in key:
                        matched_category = category
                        matched_device = device
                        break
                
                if matched_category and matched_device:
                    self.log_message(f"🔍 Searching for: {matched_category} > {matched_device}")
                    
                    # Improved browser navigation
                    if hasattr(browser, 'load_item'):
                        # Get browser sections
                        sections = {
                            'instruments': browser.instruments if hasattr(browser, 'instruments') else None,
                            'audio_effects': browser.audio_effects if hasattr(browser, 'audio_effects') else None,
                            'midi_effects': browser.midi_effects if hasattr(browser, 'midi_effects') else None,
                            'drums': browser.drums if hasattr(browser, 'drums') else None,
                        }
                        
                        # Find matching section
                        section = None
                        if 'Instruments' in matched_category:
                            section = sections.get('instruments')
                        elif 'Audio Effects' in matched_category:
                            section = sections.get('audio_effects')
                        elif 'MIDI Effects' in matched_category:
                            section = sections.get('midi_effects')
                        elif 'Drums' in matched_category:
                            section = sections.get('drums')
                        
                        if section:
                            # Search for device in section
                            for item in section:
                                if hasattr(item, 'name') and matched_device.lower() in str(item.name).lower():
                                    self.log_message(f"✅ Found device: {item.name}")
                                    # Load to track
                                    if hasattr(track, 'view') and hasattr(track.view, 'select_device'):
                                        track.view.selected_device = item  # Attempt to select
                                    else:
                                        browser.load_item(item)  # Fallback load
                                        self.log_message(f"🎹 Loaded {matched_device} to track {track_idx}")
                                        return
                        
                    # Fallback to basic creation if browser fails
                        self._create_basic_device(track, device_name, matched_device)
                        
                else:
                    self.log_message(f"⚠️ Device '{device_name}' not found in mappings")
                    self.log_message(f"💡 Try common names like: kick, reverb, eq eight, compressor")
                    
            except Exception as browser_error:
                self.log_message(f"⚠️ Browser error: {browser_error}")
                self._create_basic_device(track, device_name, device_name)
                
        except Exception as e:
            self.log_message(f"❌ Failed to add device: {e}")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}")
    
    def _create_basic_device(self, track, device_query, device_name):
        """Fallback method - create MIDI pattern for drums or try to create basic instruments"""
        try:
            self.log_message(f"🔧 Attempting to create device: {device_name}")

            # For drum sounds (kick, snare, etc), create MIDI clip with pattern
            drum_keywords = ['kick', 'snare', 'hat', 'hi-hat', 'clap', 'rim', 'tom', 'cymbal', 'crash']

            is_drum = any(keyword in device_query for keyword in drum_keywords)

            if is_drum and hasattr(track, 'clip_slots'):
                # Find empty clip slot
                for slot_idx, clip_slot in enumerate(track.clip_slots):
                    if not clip_slot.has_clip:
                        # Create MIDI clip
                        clip_slot.create_clip(4.0)  # 4 beats
                        clip = clip_slot.clip

                        # Add notes based on drum type
                        if 'kick' in device_query:
                            # Kick drum pattern: C1 (note 36) on every beat
                            self._add_drum_pattern(clip, 36, [0, 1, 2, 3], "kick")
                        elif 'snare' in device_query:
                            # Snare: D1 (note 38) on beats 2 and 4
                            self._add_drum_pattern(clip, 38, [1, 3], "snare")
                        elif 'hat' in device_query or 'hi-hat' in device_query:
                            # Hi-hat: F#1 (note 42) on every 1/8th note
                            self._add_drum_pattern(clip, 42, [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5], "hi-hat")
                        else:
                            # Generic drum note
                            self._add_drum_pattern(clip, 36, [0, 1, 2, 3], "drum")

                        self.log_message(f"✅ Created MIDI pattern for {device_query}")
                        self.log_message(f"💡 Add Drum Rack or drum instrument to hear sound!")
                        return

                self.log_message(f"⚠️ No empty clip slots available")
            else:
                # Try to create basic instruments directly
                if self._try_create_basic_instrument(track, device_query, device_name):
                    return

                # For non-drum devices, just log
                self.log_message(f"📝 Device '{device_name}' requested on track '{track.name}'")
                self.log_message(f"💡 Please add '{device_name}' manually from Ableton's browser")
                self.log_message(f"💡 Drag & drop from: Instruments or Audio Effects")

        except Exception as e:
            self.log_message(f"❌ Fallback creation failed: {e}")

    def _try_create_basic_instrument(self, track, device_query, device_name):
        """Try to create basic instruments directly using Live Object Model"""
        try:
            # Map common device names to creation methods
            instrument_mappings = {
                'simpler': self._create_simpler,
                'sampler': self._create_simpler,  # Simpler can act as sampler
                'drum rack': self._create_drum_rack,
                'operator': self._create_operator,
                'analog': self._create_analog,
                'collision': self._create_collision,
                'electric': self._create_electric,
                'tension': self._create_tension,
                'wavetable': self._create_wavetable,
                'impulse': self._create_impulse,
            }

            # Check if we can create this instrument
            for key, create_func in instrument_mappings.items():
                if key in device_query.lower():
                    self.log_message(f"🎹 Attempting to create {key} instrument...")
                    success = create_func(track)
                    if success:
                        self.log_message(f"✅ Successfully created {key} on track '{track.name}'")
                        return True

            return False

        except Exception as e:
            self.log_message(f"⚠️ Failed to create instrument: {e}")
            return False

    def _create_simpler(self, track):
        """Try to create Simpler instrument"""
        try:
            # Try to create Simpler using Live Object Model (experimental)
            # This may not work in all Ableton versions
            song = self.song()

            # Check if we can access the application and browser
            app = self.application()
            if hasattr(app, 'get_device'):
                # Try to get Simpler from the application
                try:
                    simpler_device = app.get_device('Simpler')
                    if simpler_device:
                        # Try to add it to track
                        track.add_device(simpler_device)
                        return True
                except:
                    pass

            # Alternative: Try browser approach with different method
            if hasattr(app, 'browser'):
                browser = app.browser
                try:
                    # Try to navigate to Simpler
                    if hasattr(browser, 'instruments'):
                        instruments = browser.instruments
                        if instruments and len(instruments) > 0:
                            # Look for Simpler
                            for item in instruments:
                                if hasattr(item, 'name') and 'Simpler' in str(item.name):
                                    browser.load_item(item)
                                    return True
                except:
                    pass

            # Fallback: Give detailed instructions
            self.log_message("💡 Simpler creation requires manual addition:")
            self.log_message("1. Click on track header to select track")
            self.log_message("2. Go to Browser > Instruments > Simpler")
            self.log_message("3. Drag Simpler to the track")
            self.log_message("4. Load a sample: Right-click Simpler > Load Sample")
            return False
        except Exception as e:
            self.log_message(f"⚠️ Simpler creation error: {e}")
            return False

    def _create_drum_rack(self, track):
        """Try to create Drum Rack"""
        try:
            # Try experimental Drum Rack creation
            app = self.application()
            if hasattr(app, 'browser'):
                browser = app.browser
                try:
                    # Look for Drum Rack in browser
                    if hasattr(browser, 'instruments'):
                        instruments = browser.instruments
                        if instruments:
                            for item in instruments:
                                if hasattr(item, 'name') and 'Drum Rack' in str(item.name):
                                    browser.load_item(item)
                                    return True
                except:
                    pass

            # Fallback instructions
            self.log_message("💡 Drum Rack creation requires manual addition:")
            self.log_message("1. Select the track")
            self.log_message("2. Browser > Instruments > Drum Rack")
            self.log_message("3. Drag Drum Rack to track")
            self.log_message("4. Add samples to pads (double-click pads)")
            return False
        except Exception as e:
            self.log_message(f"⚠️ Drum Rack creation error: {e}")
            return False

    def _create_operator(self, track):
        """Try to create Operator"""
        try:
            self.log_message("💡 Operator creation requires manual addition from browser")
            self.log_message("💡 Go to: Browser > Instruments > Operator")
            return False
        except Exception as e:
            return False

    def _create_analog(self, track):
        """Try to create Analog"""
        try:
            self.log_message("💡 Analog creation requires manual addition from browser")
            self.log_message("💡 Go to: Browser > Instruments > Analog")
            return False
        except Exception as e:
            return False

    def _create_collision(self, track):
        """Try to create Collision"""
        try:
            self.log_message("💡 Collision creation requires manual addition from browser")
            self.log_message("💡 Go to: Browser > Instruments > Collision")
            return False
        except Exception as e:
            return False

    def _create_electric(self, track):
        """Try to create Electric"""
        try:
            self.log_message("💡 Electric creation requires manual addition from browser")
            self.log_message("💡 Go to: Browser > Instruments > Electric")
            return False
        except Exception as e:
            return False

    def _create_tension(self, track):
        """Try to create Tension"""
        try:
            self.log_message("💡 Tension creation requires manual addition from browser")
            self.log_message("💡 Go to: Browser > Instruments > Tension")
            return False
        except Exception as e:
            return False

    def _create_wavetable(self, track):
        """Try to create Wavetable"""
        try:
            self.log_message("💡 Wavetable creation requires manual addition from browser")
            self.log_message("💡 Go to: Browser > Instruments > Wavetable")
            return False
        except Exception as e:
            return False

    def _create_impulse(self, track):
        """Try to create Impulse"""
        try:
            self.log_message("💡 Impulse creation requires manual addition from browser")
            self.log_message("💡 Go to: Browser > Instruments > Impulse")
            return False
        except Exception as e:
            return False
            
    def _add_drum_pattern(self, clip, note_number, beat_positions, drum_name):
        """Add MIDI notes to clip for drum pattern"""
        try:
            if not clip.is_midi_clip:
                return
                
            # Remove existing notes first
            clip.remove_notes(0, 0, clip.length, 127)
            
            # Add notes at specified beat positions
            for beat in beat_positions:
                # note_number, beat_time, duration, velocity, muted
                clip.set_notes(((note_number, beat, 0.25, 100, False),))
                
            self.log_message(f"✅ Added {drum_name} pattern: {len(beat_positions)} hits")
            
        except Exception as e:
            self.log_message(f"⚠️ Could not add notes: {e}")
            
    def _set_track_volume(self, command):
        """Set track volume"""
        track_idx = command.get('track_index', 0)
        volume = float(command.get('volume', 1.0))
        
        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if hasattr(track, 'mixer_device'):
                track.mixer_device.volume.value = max(0.0, min(1.0, volume))
                self.log_message(f"🔊 Track {track_idx} volume set to {volume}")
        
    def _set_track_pan(self, command):
        """Set track pan"""
        track_idx = command.get('track_index', 0)
        pan = float(command.get('pan', 0.0))
        
        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if hasattr(track, 'mixer_device'):
                track.mixer_device.panning.value = max(-1.0, min(1.0, pan))
                self.log_message(f"🎛️ Track {track_idx} pan set to {pan}")
                
    def _mute_track(self, command):
        """Mute/unmute track"""
        track_idx = command.get('track_index', 0)
        mute = command.get('mute', True)
        
        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            track.mute = bool(mute)
            self.log_message(f"🔇 Track {track_idx} mute: {mute}")
            
    def _solo_track(self, command):
        """Solo/unsolo track"""
        track_idx = command.get('track_index', 0)
        solo = command.get('solo', True)
        
        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            track.solo = bool(solo)
            self.log_message(f"🎧 Track {track_idx} solo: {solo}")
            
    def _arm_track(self, command):
        """Arm/unarm track for recording"""
        track_idx = command.get('track_index', 0)
        arm = command.get('arm', True)
        
        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if track.can_be_armed:
                track.arm = bool(arm)
                self.log_message(f"🎙️ Track {track_idx} armed: {arm}")
                
    def _create_clip(self, command):
        """Create new clip in clip slot"""
        try:
            track_idx = command.get('track_index', self.last_created_track_index)  # Use last if not specified
            slot_idx = command.get('slot_index', 0)
            length = command.get('length', 4.0)

            self.log_message(f"📝 Creating clip: track {track_idx}, slot {slot_idx}, length {length}")

            song = self.song()
            self.log_message(f"📊 Current tracks: {len(song.tracks)}")

            if track_idx < len(song.tracks):
                track = song.tracks[track_idx]
                self.log_message(f"📋 Track found: {track.name}, clip slots: {len(track.clip_slots)}")

                if slot_idx < len(track.clip_slots):
                    clip_slot = track.clip_slots[slot_idx]
                    self.log_message(f"🎵 Clip slot {slot_idx} has clip: {clip_slot.has_clip}")

                    if not clip_slot.has_clip:
                        clip_slot.create_clip(float(length))
                        self.log_message(f"✅ Created clip at track {track_idx}, slot {slot_idx}")
                    else:
                        self.log_message(f"⚠️ Clip slot {slot_idx} already has clip")
                else:
                    self.log_message(f"⚠️ Slot {slot_idx} does not exist on track {track_idx}")
            else:
                self.log_message(f"⚠️ Track {track_idx} does not exist (max: {len(song.tracks)-1})")
        except Exception as e:
            self.log_message(f"❌ create_clip failed: {e}")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}")

    def _add_notes(self, command):
        """Add MIDI notes to clip - improved version that can create clip if needed"""
        track_idx = command.get('track_index', self.last_created_track_index)  # Use last if not specified
        slot_idx = command.get('slot_index', 0)
        notes = command.get('notes', [])

        self.log_message(f"🎵 Adding notes to track {track_idx}, slot {slot_idx}")

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            self.log_message(f"📋 Track found: {track.name}")

            if slot_idx < len(track.clip_slots):
                clip_slot = track.clip_slots[slot_idx]

                # If no clip exists, create one
                if not clip_slot.has_clip:
                    self.log_message(f"📝 Creating clip in slot {slot_idx}")
                    try:
                        clip_slot.create_clip(4.0)  # 4 beats
                        self.log_message(f"✅ Clip created")
                    except Exception as e:
                        self.log_message(f"❌ Failed to create clip: {e}")
                        return

                if clip_slot.has_clip:
                    clip = clip_slot.clip
                    self.log_message(f"🎼 Clip found: {clip.name}, is_midi: {clip.is_midi_clip}")

                    if clip.is_midi_clip:
                        # Clear existing notes first - Live 12 compatible
                        try:
                            clip.remove_notes_extended(0, 128, 0, clip.length)
                            self.log_message(f"🧹 Cleared existing notes (Live 12 API)")
                        except Exception as e:
                            self.log_message(f"⚠️ Failed to clear notes: {e}")
                            # Emergency fallback - try old method
                            try:
                                clip.remove_notes(0, 0, clip.length, 127)
                                self.log_message(f"🧹 Emergency clear with legacy API")
                            except Exception as e2:
                                self.log_message(f"❌ Both clear methods failed: {e2}")

                        # Parse notes - support multiple formats and add default kick if no notes
                        note_tuples = []
                        self.log_message(f"📝 Parsing {len(notes)} notes...")
                        if not notes:
                            # Default kick pattern if no notes provided
                            notes = [[36, 0, 1, 100], [36, 2, 1, 100]]  # Basic kick on 1 and 3
                            self.log_message(f"📝 Using default kick pattern")

                        for i, note in enumerate(notes):
                            try:
                                self.log_message(f"🎵 Note {i}: {note}")

                                if isinstance(note, (list, tuple)) and len(note) >= 4:
                                    pitch = int(note[0])
                                    time = float(note[1])
                                    duration = float(note[2]) if note[2] > 0 else 0.25
                                    velocity = int(note[3])
                                    self.log_message(f"✅ Parsed array format: pitch={pitch}, time={time}, duration={duration}, vel={velocity}")
                                elif isinstance(note, dict):
                                    pitch = int(note.get('pitch', 60))
                                    time = float(note.get('time', 0))
                                    duration = float(note.get('duration', 0.25))
                                    velocity = int(note.get('velocity', 100))
                                    self.log_message(f"✅ Parsed dict format: pitch={pitch}, time={time}, duration={duration}, vel={velocity}")
                                else:
                                    self.log_message(f"⚠️ Skipping invalid note format: {note}")
                                    continue

                                note_tuples.append((pitch, time, duration, velocity, False))
                            except Exception as e:
                                self.log_message(f"❌ Failed to parse note {i}: {note}, error: {e}")
                                import traceback
                                self.log_message(f"Traceback: {traceback.format_exc()}")

                        # Add all notes at once
                        if note_tuples:
                            try:
                                clip.set_notes(tuple(note_tuples))
                                self.log_message(f"✅ Added {len(note_tuples)} notes to clip at track {track_idx}, slot {slot_idx}")
                                clip.is_playing = False
                                clip.stop()  # Stop any auto-play
                            except Exception as e:
                                self.log_message(f"❌ Failed to set notes: {e}")
                                import traceback
                                self.log_message(f"Traceback: {traceback.format_exc()}")
                        else:
                            self.log_message(f"⚠️ No valid notes to add")
                    else:
                        self.log_message(f"⚠️ Clip is not a MIDI clip")
                else:
                    self.log_message(f"⚠️ No clip at track {track_idx}, slot {slot_idx}")
            else:
                self.log_message(f"⚠️ Slot {slot_idx} does not exist on track {track_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")
                        
    def _delete_track(self, command):
        """Delete a track"""
        track_idx = command.get('track_index', 0)
        
        song = self.song()
        if track_idx < len(song.tracks):
            song.delete_track(track_idx)
            self.log_message(f"🗑️ Deleted track {track_idx}")

    def _play_clip(self, command):
        track_idx = command.get('track_index', self.last_created_track_index)
        slot_idx = command.get('slot_index', 0)
        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if slot_idx < len(track.clip_slots):
                clip_slot = track.clip_slots[slot_idx]
                if clip_slot.has_clip:
                    clip_slot.clip.fire()
                    self.log_message(f"▶️ Played clip at track {track_idx}, slot {slot_idx}")

    def _stop_clip(self, command):
        track_idx = command.get('track_index', self.last_created_track_index)
        slot_idx = command.get('slot_index', 0)
        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if slot_idx < len(track.clip_slots):
                clip_slot = track.clip_slots[slot_idx]
                if clip_slot.has_clip:
                    clip_slot.clip.stop()
                    self.log_message(f"⏹️ Stopped clip at track {track_idx}, slot {slot_idx}")

    def _group_tracks(self, command):
        """Group multiple tracks together"""
        track_indices = command.get('track_indices', [])
        group_name = command.get('name', 'Group')
        
        if not track_indices or len(track_indices) < 2:
            self.log_message("⚠️ Need at least 2 tracks to group")
            return
        
        song = self.song()
        
        # Validate track indices
        valid_indices = [i for i in track_indices if i < len(song.tracks)]
        if len(valid_indices) < 2:
            self.log_message("⚠️ Not enough valid track indices")
            return
        
        # Sort indices to ensure correct order
        valid_indices.sort()
        
        # Select the tracks for grouping
        # In Ableton, we need to select tracks first, then group them
        try:
            # Create group by selecting tracks
            tracks_to_group = [song.tracks[i] for i in valid_indices]
            
            # Ableton's group_tracks method groups consecutively selected tracks
            # We need to make sure tracks are consecutive or move them
            song.view.selected_track = tracks_to_group[0]
            
            # Group the tracks
            song.create_group_track(valid_indices[0])
            
            # Get the newly created group track
            group_track = song.tracks[valid_indices[0]]
            group_track.name = group_name
            
            self.log_message(f"📁 Grouped tracks {valid_indices} into '{group_name}'")
            return valid_indices[0]
            
        except Exception as e:
            self.log_message(f"⚠️ Group creation failed: {e}")
            self.log_message(f"💡 Try grouping tracks manually: Select tracks → Right-click → Group Tracks (Ctrl/Cmd+G)")
    
    def _ungroup_tracks(self, command):
        """Ungroup a group track"""
        track_idx = command.get('track_index', 0)
        
        song = self.song()
        if track_idx >= len(song.tracks):
            self.log_message("⚠️ Invalid track index")
            return
        
        track = song.tracks[track_idx]
        
        # Check if it's a group track
        if not track.is_foldable:
            self.log_message("⚠️ Track is not a group")
            return
        
        try:
            # Unfold if folded
            if track.fold_state == 0:
                track.fold_state = 1
            
            # Ableton's ungroup method
            song.view.selected_track = track
            
            self.log_message(f"📂 Ungrouped track {track_idx}")
            self.log_message(f"💡 Complete ungrouping manually: Select group → Right-click → Ungroup (Ctrl/Cmd+Shift+G)")
            
        except Exception as e:
            self.log_message(f"⚠️ Ungroup failed: {e}")

    # === EXTENDED TRACK MANAGEMENT FUNCTIONS ===

    def _add_return_track(self, command):
        """Add a new return track"""
        try:
            song = self.song()
            return_track = song.create_return_track()
            self.log_message(f"✅ Created return track at index {len(song.return_tracks) - 1}")
            return len(song.return_tracks) - 1
        except Exception as e:
            self.log_message(f"❌ Failed to create return track: {e}")

    def _rename_track(self, command):
        """Rename a track"""
        track_idx = command.get('track_index', 0)
        new_name = command.get('name', 'New Track')

        song = self.song()
        if track_idx < len(song.tracks):
            song.tracks[track_idx].name = str(new_name)
            self.log_message(f"✅ Renamed track {track_idx} to '{new_name}'")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _set_track_color(self, command):
        """Set track color"""
        track_idx = command.get('track_index', 0)
        color_idx = command.get('color_index', 0)  # 0-69 for Ableton colors

        song = self.song()
        if track_idx < len(song.tracks):
            try:
                song.tracks[track_idx].color_index = int(color_idx)
                self.log_message(f"✅ Set track {track_idx} color to {color_idx}")
            except Exception as e:
                self.log_message(f"⚠️ Failed to set color: {e}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _duplicate_track(self, command):
        """Duplicate a track"""
        track_idx = command.get('track_index', 0)

        song = self.song()
        if track_idx < len(song.tracks):
            try:
                song.duplicate_track(track_idx)
                new_track_idx = len(song.tracks) - 1
                self.log_message(f"✅ Duplicated track {track_idx} to new track {new_track_idx}")
                return new_track_idx
            except Exception as e:
                self.log_message(f"❌ Failed to duplicate track: {e}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _move_track(self, command):
        """Move track to new position"""
        track_idx = command.get('track_index', 0)
        new_position = command.get('new_position', 0)

        song = self.song()
        if track_idx < len(song.tracks) and new_position < len(song.tracks):
            try:
                song.move_track(track_idx, new_position)
                self.log_message(f"✅ Moved track from {track_idx} to {new_position}")
            except Exception as e:
                self.log_message(f"❌ Failed to move track: {e}")
        else:
            self.log_message(f"⚠️ Invalid track indices: {track_idx} -> {new_position}")

    # === MIDI NOTE MANIPULATION FUNCTIONS ===

    def _add_single_note(self, command):
        """Add a single note to MIDI clip"""
        track_idx = command.get('track_index', self.last_created_track_index)
        slot_idx = command.get('slot_index', 0)
        pitch = command.get('pitch', 60)
        velocity = command.get('velocity', 100)
        start_time = command.get('start_time', 0.0)
        duration = command.get('duration', 0.25)

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if slot_idx < len(track.clip_slots):
                clip_slot = track.clip_slots[slot_idx]
                if clip_slot.has_clip and clip_slot.clip.is_midi_clip:
                    clip = clip_slot.clip
                    try:
                        clip.set_notes(((pitch, start_time, duration, velocity, False),))
                        self.log_message(f"✅ Added note: pitch={pitch}, time={start_time}, dur={duration}, vel={velocity}")
                    except Exception as e:
                        self.log_message(f"❌ Failed to add note: {e}")
                else:
                    self.log_message(f"⚠️ No MIDI clip at track {track_idx}, slot {slot_idx}")
            else:
                self.log_message(f"⚠️ Invalid slot index {slot_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _delete_notes(self, command):
        """Delete notes from a time range in MIDI clip"""
        track_idx = command.get('track_index', self.last_created_track_index)
        slot_idx = command.get('slot_index', 0)
        start_time = command.get('start_time', 0.0)
        end_time = command.get('end_time', 4.0)
        pitch_min = command.get('pitch_min', 0)
        pitch_max = command.get('pitch_max', 127)

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if slot_idx < len(track.clip_slots):
                clip_slot = track.clip_slots[slot_idx]
                if clip_slot.has_clip and clip_slot.clip.is_midi_clip:
                    clip = clip_slot.clip
                    try:
                        clip.remove_notes_extended(pitch_min, pitch_max, start_time, end_time)
                        self.log_message(f"✅ Deleted notes from {start_time}-{end_time}s, pitch {pitch_min}-{pitch_max}")
                    except Exception as e:
                        self.log_message(f"❌ Failed to delete notes: {e}")
                else:
                    self.log_message(f"⚠️ No MIDI clip at track {track_idx}, slot {slot_idx}")
            else:
                self.log_message(f"⚠️ Invalid slot index {slot_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _transpose_notes(self, command):
        """Transpose all notes in a MIDI clip"""
        track_idx = command.get('track_index', self.last_created_track_index)
        slot_idx = command.get('slot_index', 0)
        semitones = command.get('semitones', 0)

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if slot_idx < len(track.clip_slots):
                clip_slot = track.clip_slots[slot_idx]
                if clip_slot.has_clip and clip_slot.clip.is_midi_clip:
                    clip = clip_slot.clip
                    try:
                        # Get all notes
                        notes = list(clip.get_notes_extended(0, 127, 0, clip.length))
                        if notes:
                            # Transpose pitches
                            transposed_notes = []
                            for note in notes:
                                new_pitch = max(0, min(127, note[0] + semitones))
                                transposed_notes.append((new_pitch, note[1], note[2], note[3], note[4]))

                            # Clear and re-add notes
                            clip.remove_notes_extended(0, 127, 0, clip.length)
                            clip.set_notes(tuple(transposed_notes))
                            self.log_message(f"✅ Transposed {len(notes)} notes by {semitones} semitones")
                        else:
                            self.log_message(f"⚠️ No notes found to transpose")
                    except Exception as e:
                        self.log_message(f"❌ Failed to transpose notes: {e}")
                else:
                    self.log_message(f"⚠️ No MIDI clip at track {track_idx}, slot {slot_idx}")
            else:
                self.log_message(f"⚠️ Invalid slot index {slot_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _humanize_notes(self, command):
        """Add human feel to notes by randomizing velocity and timing"""
        import random

        track_idx = command.get('track_index', self.last_created_track_index)
        slot_idx = command.get('slot_index', 0)
        velocity_variation = command.get('velocity_variation', 0.1)  # ±10%
        timing_variation = command.get('timing_variation', 0.05)  # ±5%

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if slot_idx < len(track.clip_slots):
                clip_slot = track.clip_slots[slot_idx]
                if clip_slot.has_clip and clip_slot.clip.is_midi_clip:
                    clip = clip_slot.clip
                    try:
                        notes = list(clip.get_notes_extended(0, 127, 0, clip.length))
                        if notes:
                            humanized_notes = []
                            for note in notes:
                                # Humanize velocity
                                vel_variation = int(note[3] * velocity_variation)
                                new_vel = max(1, min(127, note[3] + random.randint(-vel_variation, vel_variation)))

                                # Humanize timing
                                time_variation = note[2] * timing_variation  # Based on note duration
                                new_time = max(0, note[1] + random.uniform(-time_variation, time_variation))

                                humanized_notes.append((note[0], new_time, note[2], new_vel, note[4]))

                            clip.remove_notes_extended(0, 127, 0, clip.length)
                            clip.set_notes(tuple(humanized_notes))
                            self.log_message(f"✅ Humanized {len(notes)} notes (vel: ±{velocity_variation*100}%, time: ±{timing_variation*100}%)")
                        else:
                            self.log_message(f"⚠️ No notes found to humanize")
                    except Exception as e:
                        self.log_message(f"❌ Failed to humanize notes: {e}")
                else:
                    self.log_message(f"⚠️ No MIDI clip at track {track_idx}, slot {slot_idx}")
            else:
                self.log_message(f"⚠️ Invalid slot index {slot_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _quantize_notes(self, command):
        """Quantize notes to grid"""
        track_idx = command.get('track_index', self.last_created_track_index)
        slot_idx = command.get('slot_index', 0)
        grid_size = command.get('grid_size', 0.25)  # 1/16th notes by default

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if slot_idx < len(track.clip_slots):
                clip_slot = track.clip_slots[slot_idx]
                if clip_slot.has_clip and clip_slot.clip.is_midi_clip:
                    clip = clip_slot.clip
                    try:
                        notes = list(clip.get_notes_extended(0, 127, 0, clip.length))
                        if notes:
                            quantized_notes = []
                            for note in notes:
                                # Quantize start time to nearest grid
                                quantized_time = round(note[1] / grid_size) * grid_size
                                quantized_notes.append((note[0], quantized_time, note[2], note[3], note[4]))

                            clip.remove_notes_extended(0, 127, 0, clip.length)
                            clip.set_notes(tuple(quantized_notes))
                            self.log_message(f"✅ Quantized {len(notes)} notes to {grid_size} grid")
                        else:
                            self.log_message(f"⚠️ No notes found to quantize")
                    except Exception as e:
                        self.log_message(f"❌ Failed to quantize notes: {e}")
                else:
                    self.log_message(f"⚠️ No MIDI clip at track {track_idx}, slot {slot_idx}")
            else:
                self.log_message(f"⚠️ Invalid slot index {slot_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _create_drum_pattern(self, command):
        """Create a basic drum pattern"""
        track_idx = command.get('track_index', self.last_created_track_index)
        pattern_type = command.get('pattern_type', 'basic')  # basic, rock, funk
        bars = command.get('bars', 1)

        patterns = {
            'basic': {
                'kick': [0, 2],  # 1 and 3
                'snare': [1, 3],  # 2 and 4
                'hihat': [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]  # every 8th note
            },
            'rock': {
                'kick': [0, 1.5, 2, 3],
                'snare': [1, 3],
                'hihat': [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]
            },
            'funk': {
                'kick': [0, 1, 2, 3],
                'snare': [1, 2.75],
                'hihat': [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]
            }
        }

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            # Find empty clip slot
            for slot_idx in range(len(track.clip_slots)):
                if not track.clip_slots[slot_idx].has_clip:
                    clip_slot = track.clip_slots[slot_idx]
                    clip_slot.create_clip(bars * 4.0)  # 4 beats per bar
                    clip = clip_slot.clip

                    if clip.is_midi_clip:
                        pattern_notes = []
                        drum_map = {'kick': 36, 'snare': 38, 'hihat': 42}  # GM drum notes

                        for drum, positions in patterns[pattern_type].items():
                            if drum in drum_map:
                                for pos in positions:
                                    # Repeat for each bar
                                    for bar in range(bars):
                                        time = bar * 4.0 + pos
                                        pattern_notes.append((drum_map[drum], time, 0.25, 100, False))

                        clip.set_notes(tuple(pattern_notes))
                        self.log_message(f"✅ Created {pattern_type} drum pattern with {len(pattern_notes)} hits over {bars} bars")
                        return slot_idx
                    else:
                        self.log_message(f"⚠️ Created clip is not MIDI")
                    break
            else:
                self.log_message(f"⚠️ No empty clip slots found on track {track_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    # === DEVICE MANAGEMENT FUNCTIONS ===

    def _remove_device(self, command):
        """Remove a device from track"""
        track_idx = command.get('track_index', 0)
        device_idx = command.get('device_index', 0)

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if device_idx < len(track.devices):
                device = track.devices[device_idx]
                device_name = device.name
                try:
                    track.remove_device(device)
                    self.log_message(f"✅ Removed device '{device_name}' from track {track_idx}")
                except Exception as e:
                    self.log_message(f"❌ Failed to remove device: {e}")
            else:
                self.log_message(f"⚠️ Device {device_idx} not found on track {track_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _toggle_device(self, command):
        """Toggle device on/off"""
        track_idx = command.get('track_index', 0)
        device_idx = command.get('device_index', 0)
        enabled = command.get('enabled', True)

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if device_idx < len(track.devices):
                device = track.devices[device_idx]
                try:
                    device.is_active = bool(enabled)
                    status = "enabled" if enabled else "disabled"
                    self.log_message(f"✅ {status} device '{device.name}' on track {track_idx}")
                except Exception as e:
                    self.log_message(f"❌ Failed to toggle device: {e}")
            else:
                self.log_message(f"⚠️ Device {device_idx} not found on track {track_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _set_device_parameter(self, command):
        """Set device parameter value"""
        track_idx = command.get('track_index', 0)
        device_idx = command.get('device_index', 0)
        param_name = command.get('parameter_name', '')
        param_value = command.get('parameter_value', 0.0)

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if device_idx < len(track.devices):
                device = track.devices[device_idx]
                try:
                    # Find parameter by name
                    for param in device.parameters:
                        if param.name.lower() == param_name.lower():
                            param.value = float(param_value)
                            self.log_message(f"✅ Set {param_name} to {param_value} on '{device.name}'")
                            return
                    self.log_message(f"⚠️ Parameter '{param_name}' not found on device '{device.name}'")
                except Exception as e:
                    self.log_message(f"❌ Failed to set parameter: {e}")
            else:
                self.log_message(f"⚠️ Device {device_idx} not found on track {track_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _set_send_level(self, command):
        """Set send level to return track"""
        track_idx = command.get('track_index', 0)
        return_track_idx = command.get('return_track_index', 0)
        send_level = command.get('send_level', 0.0)

        song = self.song()
        if track_idx < len(song.tracks) and return_track_idx < len(song.return_tracks):
            track = song.tracks[track_idx]
            return_track = song.return_tracks[return_track_idx]
            try:
                # Find the send parameter for this return track
                for param in track.mixer_device.sends:
                    if hasattr(param, 'destination') and param.destination == return_track.mixer_device:
                        param.value = float(send_level)
                        self.log_message(f"✅ Set send level to return track {return_track_idx} to {send_level}")
                        return
                self.log_message(f"⚠️ Send to return track {return_track_idx} not found")
            except Exception as e:
                self.log_message(f"❌ Failed to set send level: {e}")
        else:
            self.log_message(f"⚠️ Invalid track/return indices: {track_idx}/{return_track_idx}")

    def _load_device_preset(self, command):
        """Load device preset (if available)"""
        track_idx = command.get('track_index', 0)
        device_idx = command.get('device_index', 0)
        preset_name = command.get('preset_name', '')

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if device_idx < len(track.devices):
                device = track.devices[device_idx]
                try:
                    # Try to load preset by name
                    if hasattr(device, 'load_preset') and preset_name:
                        device.load_preset(preset_name)
                        self.log_message(f"✅ Loaded preset '{preset_name}' on '{device.name}'")
                    else:
                        self.log_message(f"⚠️ Preset loading not supported for '{device.name}' or preset '{preset_name}' not found")
                except Exception as e:
                    self.log_message(f"❌ Failed to load preset: {e}")
            else:
                self.log_message(f"⚠️ Device {device_idx} not found on track {track_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    # === BONUS FEATURES ===

    def _record_audio(self, command):
        """Record audio on a track for specified time"""
        track_idx = command.get('track_index', 0)
        duration = command.get('duration', 4.0)  # seconds
        start_immediately = command.get('start_immediately', True)

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if track.can_be_armed:
                try:
                    # Arm the track
                    track.arm = True

                    # Start recording if requested
                    if start_immediately:
                        song.record_mode = True
                        if not song.is_playing:
                            song.start_playing()

                        # Stop after duration (basic implementation)
                        import threading
                        def stop_recording():
                            time.sleep(duration)
                            song.stop_playing()
                            song.record_mode = False
                            track.arm = False
                            self.log_message(f"✅ Finished recording on track {track_idx}")

                        timer = threading.Thread(target=stop_recording)
                        timer.daemon = True
                        timer.start()

                        self.log_message(f"🎤 Started recording on track {track_idx} for {duration}s")
                    else:
                        self.log_message(f"🎤 Armed track {track_idx} for recording (start manually)")
                except Exception as e:
                    self.log_message(f"❌ Failed to start recording: {e}")
            else:
                self.log_message(f"⚠️ Track {track_idx} cannot be armed for recording")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _export_audio(self, command):
        """Export audio from arrangement or session"""
        export_type = command.get('export_type', 'arrangement')  # arrangement or session
        file_path = command.get('file_path', '')  # optional custom path
        include_limiter = command.get('include_limiter', True)

        try:
            song = self.song()

            if export_type == 'arrangement':
                # Export from arrangement view
                if file_path:
                    song.export_audio(file_path, include_limiter)
                else:
                    # Use default path
                    project_path = song.file_path if hasattr(song, 'file_path') else ''
                    if project_path:
                        export_path = project_path.replace('.als', '_export.wav')
                        song.export_audio(export_path, include_limiter)
                        self.log_message(f"✅ Exported arrangement to: {export_path}")
                    else:
                        self.log_message(f"⚠️ Project not saved, cannot determine export path")
            else:
                self.log_message(f"⚠️ Export type '{export_type}' not yet supported")

        except Exception as e:
            self.log_message(f"❌ Failed to export audio: {e}")

    def _undo_action(self, command):
        """Undo last action"""
        try:
            song = self.song()
            if hasattr(song, 'undo'):
                song.undo()
                self.log_message(f"✅ Undid last action")
            else:
                self.log_message(f"⚠️ Undo not available in this Live version")
        except Exception as e:
            self.log_message(f"❌ Failed to undo: {e}")

    def _save_snapshot(self, command):
        """Save current state as snapshot"""
        snapshot_name = command.get('name', f'Snapshot_{int(time.time())}')

        try:
            song = self.song()
            # In Ableton, we can use the built-in snapshot feature
            if hasattr(song, 'capture_and_insert_scene'):
                # Create a new scene and capture current state
                scene_idx = len(song.scenes)
                song.capture_and_insert_scene()
                if scene_idx < len(song.scenes):
                    song.scenes[scene_idx].name = snapshot_name
                    self.log_message(f"✅ Saved snapshot '{snapshot_name}' as scene {scene_idx}")
            else:
                self.log_message(f"⚠️ Snapshot feature not available")
        except Exception as e:
            self.log_message(f"❌ Failed to save snapshot: {e}")

    def _set_loop_markers(self, command):
        """Set loop start and end points"""
        start_time = command.get('start_time', 0.0)
        end_time = command.get('end_time', 4.0)
        loop_enabled = command.get('loop_enabled', True)

        try:
            song = self.song()
            song.loop_start = float(start_time)
            song.loop_length = float(end_time - start_time)
            song.loop = bool(loop_enabled)

            status = "enabled" if loop_enabled else "disabled"
            self.log_message(f"✅ Set loop markers: {start_time}-{end_time}s ({status})")
        except Exception as e:
            self.log_message(f"❌ Failed to set loop markers: {e}")

    def _consolidate_clip(self, command):
        """Consolidate/Flatten clip to audio"""
        track_idx = command.get('track_index', 0)
        slot_idx = command.get('slot_index', 0)

        song = self.song()
        if track_idx < len(song.tracks):
            track = song.tracks[track_idx]
            if slot_idx < len(track.clip_slots):
                clip_slot = track.clip_slots[slot_idx]
                if clip_slot.has_clip:
                    try:
                        # Flatten/consolidate the clip
                        clip_slot.clip.consolidate()  # This converts MIDI to audio
                        self.log_message(f"✅ Consolidated clip at track {track_idx}, slot {slot_idx}")
                    except Exception as e:
                        self.log_message(f"❌ Failed to consolidate clip: {e}")
                else:
                    self.log_message(f"⚠️ No clip at track {track_idx}, slot {slot_idx}")
            else:
                self.log_message(f"⚠️ Invalid slot index {slot_idx}")
        else:
            self.log_message(f"⚠️ Track {track_idx} does not exist")

    def _execute_mcp_tool(self, tool_name, tool_input):
        """Execute MCP tool and return result"""
        try:
            self.log_message(f"🔧 Executing MCP Tool: {tool_name}")

            # Map tool names to existing methods
            tool_mapping = {
                # === TRACK MANAGEMENT ===
                "add_return_track": self._add_return_track,
                "rename_track": self._rename_track,
                "set_track_color": self._set_track_color,
                "duplicate_track": self._duplicate_track,
                "move_track": self._move_track,
                "delete_track": self._delete_track,
                "create_midi_track": lambda cmd: self._create_track('midi', cmd),
                "create_audio_track": lambda cmd: self._create_track('audio', cmd),

                # === MIDI & NOTES ===
                "add_single_note": self._add_single_note,
                "create_drum_pattern": self._create_drum_pattern,
                "delete_notes": self._delete_notes,
                "transpose_notes": self._transpose_notes,
                "humanize_notes": self._humanize_notes,
                "quantize_notes": self._quantize_notes,
                "create_clip": self._create_clip,
                "add_notes": self._add_notes,  # bulk notes
                "play_clip": self._play_clip,
                "stop_clip": self._stop_clip,

                # === DEVICES & EFFECTS ===
                "add_device": self._add_device,
                "remove_device": self._remove_device,
                "toggle_device": self._toggle_device,
                "set_device_parameter": self._set_device_parameter,
                "set_send_level": self._set_send_level,
                "load_device_preset": self._load_device_preset,

                # === TRANSPORT & CONTROL ===
                "set_tempo": self._set_tempo,
                "play": lambda cmd: (self._transport_play(), None)[-1],
                "stop": lambda cmd: (self._transport_stop(), None)[-1],
                "record": lambda cmd: (self._transport_record(cmd), None)[-1],

                # === MIX CONTROL ===
                "set_track_volume": self._set_track_volume,
                "set_track_pan": self._set_track_pan,
                "mute_track": self._mute_track,
                "solo_track": self._solo_track,
                "arm_track": self._arm_track,

                # === BONUS FEATURES ===
                "record_audio": self._record_audio,
                "export_audio": self._export_audio,
                "undo_action": self._undo_action,
                "save_snapshot": self._save_snapshot,
                "set_loop_markers": self._set_loop_markers,
                "consolidate_clip": self._consolidate_clip,

                # === ADVANCED ===
                "group_tracks": self._group_tracks,
                "ungroup_tracks": self._ungroup_tracks,
                "set_track_pan": self._set_track_pan,
                "solo_track": self._solo_track,
                "arm_track": self._arm_track,
                "delete_track": self._delete_track,
                "create_clip": self._create_clip,
                "add_notes": self._add_notes,
                "play_clip": self._play_clip,
                "stop_clip": self._stop_clip,
                "consolidate_clip": self._consolidate_clip,
                "undo_action": self._undo_action,
                "save_snapshot": self._save_snapshot,
                "set_loop_markers": self._set_loop_markers,
                "record_audio": self._record_audio,
                "export_audio": self._export_audio,
                "remove_device": self._remove_device,
                "toggle_device": self._toggle_device,
                "set_send_level": self._set_send_level,
                "load_device_preset": self._load_device_preset,
                "delete_notes": self._delete_notes,
                "transpose_notes": self._transpose_notes,
                "humanize_notes": self._humanize_notes,
                "quantize_notes": self._quantize_notes,
                "set_track_color": self._set_track_color,
            }

            if tool_name in tool_mapping:
                # Create command dict from tool_input
                command = {"action": tool_name, **tool_input}

                # Execute the tool
                result = tool_mapping[tool_name](command)

                self.log_message(f"✅ MCP Tool {tool_name} executed successfully")
                return {"success": True, "result": result}
            else:
                self.log_message(f"⚠️ Unknown MCP tool: {tool_name}")
                return {"success": False, "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            self.log_message(f"❌ MCP Tool execution failed: {e}")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    def _on_song_changed(self):
        """Handler for when song tracks change (new set loaded)"""
        self.log_message("🔄 Detected song change - attempting reconnect...")
        self.disconnect()  # Clean up existing connections
        self.connect_script()  # Reinitialize


def create_instance(c_instance):
    """Factory function for Ableton to create the control surface"""
    return AICopilotControlSurface(c_instance)






