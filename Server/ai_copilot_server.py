# Profesor Abelton Server
# Multi-LLM Support: GPT-4, Claude, Grok, Groq, Ollama
# Version: 2.0.0

import socket
import json
import threading
import time
import os
import sys
from datetime import datetime

# Try importing required libraries
try:
    import requests
except ImportError:
    print("[!] 'requests' not installed. Run: pip install requests")
    sys.exit(1)

try:
    import speech_recognition as sr
except ImportError:
    print("[!] 'speech_recognition' not installed. Run: pip install SpeechRecognition")
    sr = None

try:
    from gtts import gTTS
    import pygame
except ImportError:
    print("[!] Voice output not available. Run: pip install gtts pygame")
    gTTS = None
    pygame = None

try:
    from pythonosc import udp_client
    from pythonosc import dispatcher
    from pythonosc import osc_server
    OSC_AVAILABLE = True
except ImportError:
    print("[!] OSC communication not available. Run: pip install python-osc")
    OSC_AVAILABLE = False


class AIConfig:
    """Configuration manager for AI providers"""
    
    def __init__(self, config_path=None):
        # Find config file relative to script or in Config folder.
        # If a provided path doesn't exist, fall back to auto-detection.
        if config_path is not None and not os.path.exists(config_path):
            config_path = None

        if config_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                # Preferred: project-root Config (robust vs current working directory)
                os.path.join(script_dir, "..", "Config", "copilot_config.json"),
                # PyInstaller onedir: config next to executable
                os.path.join(os.path.dirname(sys.executable), "Config", "copilot_config.json") if getattr(sys, "frozen", False) else "",
                # Local server folder copy (rare)
                os.path.join(script_dir, "copilot_config.json"),
                # Relative fallbacks (if user runs from project root)
                os.path.join("Config", "copilot_config.json"),
                "copilot_config.json",
            ]

            for path in possible_paths:
                if path and os.path.exists(path):
                    config_path = path
                    break

            if config_path is None:
                config_path = possible_paths[0]  # Default to first option
        
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[!] Config file not found: {self.config_path}")
            return self.default_config()
        except Exception as e:
            print(f"[!] Error loading config: {e}")
            return self.default_config()
    
    def default_config(self):
        """Return default configuration"""
        return {
            "server": {
                "host": "localhost",
                "port": 8766
            },
            "ai_providers": {
                "default": "GROQ",
                "models": {
                    "GPT": "gpt-4o-mini",
                    # Keep in sync with Config/copilot_config.json defaults
                    "CLAUDE": "claude-opus-4-20250514",
                    "GROK": "grok-beta",
                    "GROQ": "llama-3.3-70b-versatile",
                    "OLLAMA": "llama3.1"
                },
                "api_urls": {
                    "GPT": "https://api.openai.com/v1/chat/completions",
                    "CLAUDE": "https://api.anthropic.com/v1/messages",
                    "GROK": "https://api.x.ai/v1/chat/completions",
                    "GROQ": "https://api.groq.com/openai/v1/chat/completions",
                    "OLLAMA": "http://localhost:11434/api/generate"
                }
            },
            "voice": {
                "enabled": True,
                "language": "en",
                "alternative_language": "hr",
                "timeout": 5,
                "energy_threshold": 300
            }
        }
    
    def get(self, *keys):
        """Get nested config value"""
        result = self.config
        for key in keys:
            result = result.get(key, {})
        return result


class LLMProvider:
    """Multi-LLM provider with fallback support"""

    def __init__(self, config):
        self.config = config
        self.provider = config.get("ai_providers", "default").upper()
        self.api_keys = {
            "GPT": os.getenv("OPENAI_API_KEY", ""),
            "CLAUDE": os.getenv("CLAUDE_API_KEY", ""),
            "GROK": os.getenv("GROK_API_KEY", ""),
            "GROQ": os.getenv("GROQ_API_KEY", ""),
        }

        # MCP Tools for Claude (Ableton functions)
        self.mcp_tools = self._define_ableton_tools()

    def _define_ableton_tools(self):
        """Define MCP tools for Ableton Live integration"""
        return [
            # Track Management Tools
            {
                "name": "add_return_track",
                "description": "Create a new return track in Ableton",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "rename_track",
                "description": "Rename a track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index to rename"},
                        "name": {"type": "string", "description": "New track name"}
                    },
                    "required": ["track_index", "name"]
                }
            },
            {
                "name": "duplicate_track",
                "description": "Duplicate a track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index to duplicate"}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "create_midi_track",
                "description": "Create a new MIDI track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "position": {"type": "integer", "description": "Position to insert track (-1 for end)", "default": -1},
                        "name": {"type": "string", "description": "Track name", "default": "MIDI Track"}
                    },
                    "required": []
                }
            },
            {
                "name": "create_audio_track",
                "description": "Create a new audio track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "position": {"type": "integer", "description": "Position to insert track (-1 for end)", "default": -1},
                        "name": {"type": "string", "description": "Track name", "default": "Audio Track"}
                    },
                    "required": []
                }
            },

            # MIDI Tools
            {
                "name": "add_single_note",
                "description": "Add a single MIDI note to a clip",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "slot_index": {"type": "integer", "description": "Clip slot index", "default": 0},
                        "pitch": {"type": "integer", "description": "Note pitch (0-127)", "default": 60},
                        "velocity": {"type": "integer", "description": "Note velocity (0-127)", "default": 100},
                        "start_time": {"type": "number", "description": "Start time in beats", "default": 0.0},
                        "duration": {"type": "number", "description": "Note duration in beats", "default": 0.25}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "create_drum_pattern",
                "description": "Create a drum pattern (kick, snare, hi-hat)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index for drums"},
                        "pattern_type": {"type": "string", "description": "Pattern type", "enum": ["basic", "rock", "funk"], "default": "basic"},
                        "bars": {"type": "integer", "description": "Number of bars", "default": 1}
                    },
                    "required": ["track_index"]
                }
            },

            # Device & Effects Tools
            {
                "name": "add_device",
                "description": "Add an audio effect or instrument to a track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "device_name": {"type": "string", "description": "Device name (reverb, delay, eq_eight, compressor, etc.)"},
                        "device_type": {"type": "string", "description": "Device type", "enum": ["instrument", "audio_effect", "midi_effect"], "default": "audio_effect"}
                    },
                    "required": ["track_index", "device_name"]
                }
            },
            {
                "name": "set_device_parameter",
                "description": "Set a device parameter value",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "device_index": {"type": "integer", "description": "Device index on track", "default": 0},
                        "parameter_name": {"type": "string", "description": "Parameter name (e.g., 'Frequency', 'Gain', 'Threshold')"},
                        "parameter_value": {"type": "number", "description": "Parameter value"}
                    },
                    "required": ["track_index", "parameter_name", "parameter_value"]
                }
            },

            # Transport & Control
            {
                "name": "set_tempo",
                "description": "Set project tempo",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "bpm": {"type": "number", "description": "Tempo in BPM", "minimum": 20, "maximum": 999}
                    },
                    "required": ["bpm"]
                }
            },
            {
                "name": "play",
                "description": "Start playback",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "stop",
                "description": "Stop playback",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },

            # Mix Control
            {
                "name": "set_track_volume",
                "description": "Set track volume",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "volume": {"type": "number", "description": "Volume (0.0 to 1.0)", "minimum": 0.0, "maximum": 1.0}
                    },
                    "required": ["track_index", "volume"]
                }
            },
            {
                "name": "mute_track",
                "description": "Mute or unmute a track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "mute": {"type": "boolean", "description": "Mute state", "default": True}
                    },
                    "required": ["track_index"]
                }
            },
            # === EXTENDED MIDI TOOLS ===
            {
                "name": "delete_notes",
                "description": "Delete notes from a time range in MIDI clip",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "slot_index": {"type": "integer", "description": "Clip slot index", "default": 0},
                        "start_time": {"type": "number", "description": "Start time in beats", "default": 0.0},
                        "end_time": {"type": "number", "description": "End time in beats", "default": 4.0}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "transpose_notes",
                "description": "Transpose all notes in a MIDI clip",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "slot_index": {"type": "integer", "description": "Clip slot index", "default": 0},
                        "semitones": {"type": "integer", "description": "Number of semitones to transpose", "default": 0}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "quantize_notes",
                "description": "Quantize notes to grid",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "slot_index": {"type": "integer", "description": "Clip slot index", "default": 0},
                        "grid_size": {"type": "number", "description": "Grid size (e.g., 0.25 for 16th notes)", "default": 0.25}
                    },
                    "required": ["track_index"]
                }
            },
            # === EXTENDED DEVICE TOOLS ===
            {
                "name": "remove_device",
                "description": "Remove a device from track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "device_index": {"type": "integer", "description": "Device index on track", "default": 0}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "toggle_device",
                "description": "Toggle device on/off",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "device_index": {"type": "integer", "description": "Device index on track", "default": 0},
                        "enabled": {"type": "boolean", "description": "Enable/disable device", "default": True}
                    },
                    "required": ["track_index"]
                }
            },
            # === BONUS TOOLS ===
            {
                "name": "record_audio",
                "description": "Record audio on a track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index to record on"},
                        "duration": {"type": "number", "description": "Recording duration in seconds", "default": 4.0}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "export_audio",
                "description": "Export arrangement as audio",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Optional custom file path"}
                    },
                    "required": []
                }
            },
            {
                "name": "set_loop_markers",
                "description": "Set loop start and end points",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start_time": {"type": "number", "description": "Loop start time in beats", "default": 0.0},
                        "end_time": {"type": "number", "description": "Loop end time in beats", "default": 4.0},
                        "loop_enabled": {"type": "boolean", "description": "Enable/disable loop", "default": True}
                    },
                    "required": []
                }
            },
            # === COMPLETE FUNCTION COVERAGE ===
            {
                "name": "set_track_pan",
                "description": "Set track pan position",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "pan": {"type": "number", "description": "Pan position (-1.0 to 1.0)", "minimum": -1.0, "maximum": 1.0}
                    },
                    "required": ["track_index", "pan"]
                }
            },
            {
                "name": "solo_track",
                "description": "Solo or unsolo a track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "solo": {"type": "boolean", "description": "Solo state", "default": True}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "arm_track",
                "description": "Arm or disarm a track for recording",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "arm": {"type": "boolean", "description": "Arm state", "default": True}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "delete_track",
                "description": "Delete a track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index to delete"}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "create_clip",
                "description": "Create a new clip in clip slot",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "slot_index": {"type": "integer", "description": "Clip slot index", "default": 0},
                        "length": {"type": "number", "description": "Clip length in beats", "default": 4.0}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "add_notes",
                "description": "Add multiple notes to MIDI clip",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "slot_index": {"type": "integer", "description": "Clip slot index", "default": 0},
                        "notes": {
                            "type": "array",
                            "description": "Array of notes [pitch, time, duration, velocity]",
                            "items": {"type": "array", "items": {"type": "number"}}
                        }
                    },
                    "required": ["track_index", "notes"]
                }
            },
            {
                "name": "play_clip",
                "description": "Play a clip",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "slot_index": {"type": "integer", "description": "Clip slot index", "default": 0}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "stop_clip",
                "description": "Stop a clip",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "slot_index": {"type": "integer", "description": "Clip slot index", "default": 0}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "group_tracks",
                "description": "Group multiple tracks together",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_indices": {"type": "array", "description": "Array of track indices to group", "items": {"type": "integer"}},
                        "name": {"type": "string", "description": "Group name", "default": "Group"}
                    },
                    "required": ["track_indices"]
                }
            },
            {
                "name": "ungroup_tracks",
                "description": "Ungroup a group track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Group track index"}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "consolidate_clip",
                "description": "Consolidate/Flatten clip to audio",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_index": {"type": "integer", "description": "Track index"},
                        "slot_index": {"type": "integer", "description": "Clip slot index", "default": 0}
                    },
                    "required": ["track_index"]
                }
            },
            {
                "name": "undo_action",
                "description": "Undo the last action",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "save_snapshot",
                "description": "Save current state as snapshot",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Snapshot name"}
                    },
                    "required": []
                }
            }
        ]
        
    def call_llm(self, prompt, context=None):
        """Call the configured LLM provider"""
        try:
            if self.provider == "GPT":
                return self._call_openai(prompt, context)
            elif self.provider == "CLAUDE":
                return self._call_claude(prompt, context)
            elif self.provider == "GROK":
                return self._call_grok(prompt, context)
            elif self.provider == "GROQ":
                return self._call_groq(prompt, context)
            elif self.provider == "OLLAMA":
                return self._call_ollama(prompt, context)
            else:
                return {"error": f"Unknown provider: {self.provider}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _build_system_prompt(self, context):
        """Build system prompt with Ableton context"""
        system = """You are an AI assistant for Ableton Live. You help users with:
- Creating tracks, clips, and MIDI patterns
- Adjusting mix parameters (volume, pan, effects)
- Teaching music production concepts
- Troubleshooting Ableton issues
- Providing creative suggestions

When users ask you to perform actions, respond with JSON commands. Use this format:
[
    {
        "action": "create_midi_track",
        "parameters": {"position": -1}
    },
    {
        "action": "create_clip",
        "parameters": {"track_index": "LAST_CREATED", "slot_index": 0, "length": 4}
    },
    {
        "action": "add_notes",
        "parameters": {"track_index": "LAST_CREATED", "slot_index": 0, "notes": [[36, 0, 1, 100], [36, 2, 1, 100]]}
    }
]

Available actions:
- create_audio_track: {"position": -1} (adds track at end)
- create_midi_track: {"position": -1} (adds track at end)
- set_tempo: {"bpm": 120}
- play, stop, record: {}
- create_clip: {"track_index": "LAST_CREATED", "slot_index": 0, "length": 4}
- add_notes: {"track_index": "LAST_CREATED", "slot_index": 0, "notes": [[36, 0, 1, 100]]}
- mute_track: {"track_index": 0, "mute": true}  # Mute or unmute
- unmute_track: {"track_index": 0, "mute": false}  # Use for unmute
- play_clip: {"track_index": 4, "slot_index": 0} # Play specific clip
- stop_clip: {"track_index": 4, "slot_index": 0} # Stop specific clip
- group_tracks: {"track_indices": [0, 1, 2, 3], "name": "Drums"} # Group multiple tracks into folder
- ungroup_tracks: {"track_index": 0} # Ungroup a group track

Examples:
- "Unmute track 1": {"action": "mute_track", "parameters": {"track_index": 0, "mute": false}}
- "Add kick to track 5": Use track_index: 4 (tracks start at 0)
- "Pokreni traku 5": {"action": "play_clip", "parameters": {"track_index": 4, "slot_index": 0}}
- "Grupiraj trake 1, 2, 3 u folder 'Drums'": {"action": "group_tracks", "parameters": {"track_indices": [0, 1, 2], "name": "Drums"}}
- "Grupiraj sve drum trake": Identify drum tracks from current state, then use group_tracks with their indices

IMPORTANT:
- Use "LAST_CREATED" for track_index when referring to the track you just created
- Use position: -1 to add tracks at the end
- Notes format: [pitch, time, duration, velocity] where time is in beats (0, 1, 2, 3...)

For learning questions, provide helpful, beginner-friendly explanations."""
        
        if context:
            system += f"\n\nCurrent Ableton State:\n{json.dumps(context, indent=2)}"
        
        return system
    
    def _call_openai(self, prompt, context):
        """Call OpenAI GPT API"""
        api_key = self.api_keys.get("GPT")
        if not api_key:
            return {"error": "OpenAI API key not found. Set OPENAI_API_KEY environment variable."}
        
        url = self.config.get("ai_providers", "api_urls", "GPT")
        model = self.config.get("ai_providers", "models", "GPT")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": self._build_system_prompt(context)},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return {"response": content, "provider": "GPT"}
        else:
            return {"error": f"OpenAI API error: {response.status_code}"}
    
    def _call_claude(self, prompt, context):
        """Call Anthropic Claude API with MCP tool support"""
        api_key = self.api_keys.get("CLAUDE")
        if not api_key:
            return {"error": "Claude API key not found. Set CLAUDE_API_KEY environment variable."}

        url = self.config.get("ai_providers", "api_urls", "CLAUDE")
        model = self.config.get("ai_providers", "models", "CLAUDE")

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        system_prompt = self._build_system_prompt(context)

        # Check if MCP mode is enabled (can be set via config or environment)
        # Priority: Environment variable > Config file > Default (true)
        mcp_enabled_env = os.getenv("CLAUDE_MCP_ENABLED", "").lower()
        if mcp_enabled_env in ["true", "false"]:
            mcp_enabled = mcp_enabled_env == "true"
        else:
            mcp_enabled = self.config.get("mcp_enabled") if self.config.get("mcp_enabled") is not None else True

        print(f"🔧 Claude MCP Mode: {'ENABLED' if mcp_enabled else 'DISABLED'}")

        data = {
            "model": model,
            "max_tokens": 2048,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        # Add MCP tools if enabled
        if mcp_enabled:
            data["tools"] = self.mcp_tools
            data["tool_choice"] = {"type": "auto"}  # Let Claude decide when to use tools
            print(f"🔧 Added {len(self.mcp_tools)} MCP tools to Claude request")

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            return {"error": f"Claude API request failed: {str(e)}"}

        if response.status_code == 200:
            result = response.json()
            
            # Extract text content and tool calls
            text_content = ""
            tool_calls = []
            
            for content_block in result.get("content", []):
                if content_block.get("type") == "text":
                    text_content += content_block.get("text", "")
                elif content_block.get("type") == "tool_use":
                    tool_calls.append({
                        "tool_name": content_block["name"],
                        "tool_input": content_block["input"],
                        "tool_call_id": content_block["id"]
                    })

            response_data = {
                "response": text_content,
                "provider": "Claude",
                "mcp_enabled": mcp_enabled
            }

            # Convert MCP tool calls to commands for Ableton
            if tool_calls:
                commands = []
                for tc in tool_calls:
                    # Convert MCP tool call to Ableton command format
                    command = {
                        "action": tc["tool_name"],
                        "parameters": tc["tool_input"]
                    }
                    commands.append(command)
                    print(f"🔧 MCP Tool Call: {tc['tool_name']} with params: {tc['tool_input']}")
                
                response_data["commands"] = commands
                response_data["tool_calls"] = tool_calls
                response_data["response"] += f"\n\n✅ Executing {len(tool_calls)} MCP tool(s): " + ", ".join([tc["tool_name"] for tc in tool_calls])

            return response_data
        else:
            error_detail = ""
            try:
                error_data = response.json()
                error_detail = error_data.get("error", {}).get("message", "")
            except:
                error_detail = response.text[:200]
            
            error_msg = f"Claude API error {response.status_code}"
            if error_detail:
                error_msg += f": {error_detail}"
            
            # Suggest fallback for common errors
            if response.status_code == 404:
                error_msg += "\n💡 Tip: Try using GROQ or OLLAMA instead (free alternatives)"
            elif response.status_code == 401:
                error_msg += "\n💡 Tip: Check your Claude API key in Settings"
            elif response.status_code == 429:
                error_msg += "\n💡 Tip: Rate limit exceeded. Wait a moment or use GROQ"
            
            return {"error": error_msg}
    
    def _call_grok(self, prompt, context):
        """Call xAI Grok API"""
        api_key = self.api_keys.get("GROK")
        if not api_key:
            return {"error": "Grok API key not found. Set GROK_API_KEY environment variable."}
        
        url = self.config.get("ai_providers", "api_urls", "GROK")
        model = self.config.get("ai_providers", "models", "GROK")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": self._build_system_prompt(context)},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return {"response": content, "provider": "Grok"}
        else:
            return {"error": f"Grok API error: {response.status_code}"}
    
    def _call_groq(self, prompt, context):
        """Call Groq API"""
        api_key = self.api_keys.get("GROQ")
        if not api_key:
            return {"error": "Groq API key not found. Set GROQ_API_KEY environment variable."}
        
        url = self.config.get("ai_providers", "api_urls", "GROQ")
        model = self.config.get("ai_providers", "models", "GROQ")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": self._build_system_prompt(context)},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return {"response": content, "provider": "Groq"}
        else:
            return {"error": f"Groq API error: {response.status_code}"}
    
    def _call_ollama(self, prompt, context):
        """Call local Ollama API"""
        url = self.config.get("ai_providers", "api_urls", "OLLAMA")
        model = self.config.get("ai_providers", "models", "OLLAMA")
        
        full_prompt = f"{self._build_system_prompt(context)}\n\nUser: {prompt}\nAssistant:"
        
        data = {
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=data, timeout=3600)  # 1 hour for very slow computers
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "No response from Ollama")
                return {"response": content, "provider": "Ollama"}
            else:
                return {"error": f"Ollama API error: {response.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to Ollama. Make sure Ollama is running (ollama serve)"}

    def execute_mcp_tool(self, tool_name, tool_input):
        """Execute MCP tool by sending command to remote script"""
        try:
            # Create command for remote script
            command = {
                "action": tool_name,
                **tool_input  # Spread tool input as command parameters
            }

            # Send to remote script via socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((self.config.get("server", "host"), self.config.get("server", "port")))

            message = {
                "type": "mcp_tool_call",
                "tool_name": tool_name,
                "tool_input": tool_input,
                "timestamp": time.time()
            }

            sock.sendall(json.dumps(message).encode('utf-8') + b'\n')

            # Wait for response
            response_data = sock.recv(8192).decode('utf-8')
            if '\n' in response_data:
                response_data = response_data.split('\n')[0]

            response = json.loads(response_data)
            sock.close()

            if response.get("status") == "success":
                return {"success": True, "result": response.get("result", "Tool executed successfully")}
            else:
                return {"success": False, "error": response.get("error", "Unknown error")}

        except Exception as e:
            return {"success": False, "error": f"MCP tool execution failed: {str(e)}"}


class VoiceController:
    """Voice recognition and synthesis controller"""

    def __init__(self, config):
        self.config = config
        self.recognizer = sr.Recognizer() if sr else None

        # Try to initialize microphone, but don't fail if PyAudio is not available
        self.microphone = None
        if sr:
            try:
                self.microphone = sr.Microphone()
            except Exception as e:
                print(f"[!] Microphone disabled: {e}")
                self.microphone = None

        # Configure recognizer
        if self.recognizer:
            self.recognizer.energy_threshold = config.get("voice", "energy_threshold")
            self.recognizer.pause_threshold = 0.8
            
    def listen(self, language="en"):
        """Listen for voice command"""
        if not self.recognizer or not self.microphone:
            return {"error": "Voice recognition not available"}
        
        try:
            with self.microphone as source:
                print(f"🎤 Listening ({language})...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Use Google Speech Recognition
            lang_code = "en-US" if language == "en" else "hr-HR"
            text = self.recognizer.recognize_google(audio, language=lang_code)
            
            print(f"🗣️ Recognized: {text}")
            return {"text": text, "language": language}
            
        except sr.WaitTimeoutError:
            return {"error": "Listening timeout"}
        except sr.UnknownValueError:
            return {"error": "Could not understand audio"}
        except sr.RequestError as e:
            return {"error": f"Recognition service error: {e}"}
        except Exception as e:
            return {"error": f"Voice error: {e}"}
    
    def speak(self, text, language="en"):
        """Speak text using TTS"""
        if not gTTS or not pygame:
            print(f"💬 {text}")
            return
        
        try:
            # Generate speech
            lang_code = "en" if language == "en" else "hr"
            tts = gTTS(text=text, lang=lang_code)
            
            # Save to temporary file
            temp_file = "temp_voice.mp3"
            tts.save(temp_file)
            
            # Play audio
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Cleanup
            os.remove(temp_file)
            
        except Exception as e:
            print(f"⚠️ Voice output error: {e}")


class AICopilotServer:
    """Main Profesor Abelton Server"""

    def __init__(self, config_path=None):
        self.config = AIConfig(config_path)
        self.llm = LLMProvider(self.config)

        # Initialize voice controller only if dependencies are available
        try:
            self.voice = VoiceController(self.config)
            print("[i] Voice controller initialized")
        except Exception as e:
            print(f"[!] Voice controller disabled: {e}")
            self.voice = None

        self.current_state = {}
        self.chat_history = []
        self.last_ableton_update = 0  # Timestamp of last Ableton state update
        self.command_queue = []  # Queue of commands to send to Ableton
        self.last_created_track_index = -1  # Track index of last created track
        self.is_running = False

        # Server configuration
        self.host = self.config.get("server", "host")
        self.port = self.config.get("server", "port")
        self.server_socket = None

        # OSC configuration
        self.osc_enabled = OSC_AVAILABLE and self.config.get("ableton", "osc", "enabled")
        self.osc_host = self.config.get("ableton", "osc", "host")
        self.osc_ableton_port = self.config.get("ableton", "osc", "ableton_receive_port")
        self.osc_server_port = self.config.get("ableton", "osc", "server_send_port")

        # OSC clients and servers
        self.osc_client = None
        self.osc_server = None
        self.osc_server_thread = None
        
        # Connected clients
        self.gui_clients = []  # List of connected GUI clients
        self.clients_lock = threading.Lock()  # Thread-safe access to clients list
        
    def start(self):
        """Start the Profesor Abelton server"""
        self.is_running = True

        # Initialize OSC if available
        if self.osc_enabled:
            self._init_osc()
            print(f"🎛️ OSC Communication: Enabled (Ableton: {self.osc_ableton_port}, Server: {self.osc_server_port})")
        else:
            print("🎛️ OSC Communication: Disabled")

        # Create server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"🚀 Profesor Abelton Server started on {self.host}:{self.port}")
        print(f"🤖 Using LLM Provider: {self.llm.provider}")
        print(f"🎤 Voice Recognition: {'Enabled' if sr else 'Disabled'}")
        print("=" * 60)
        
        # Accept connections
        while self.is_running:
            try:
                client, address = self.server_socket.accept()
                threading.Thread(
                    target=self.handle_client,
                    args=(client, address),
                    daemon=True
                ).start()
            except KeyboardInterrupt:
                print("\n🛑 Server shutting down...")
                break
            except Exception as e:
                print(f"⚠️ Server error: {e}")
                time.sleep(1)
        
        self.stop()
    
    def _init_osc(self):
        """Initialize OSC communication"""
        try:
            # Create OSC client for sending to Ableton
            self.osc_client = udp_client.SimpleUDPClient(self.osc_host, self.osc_ableton_port)

            # Create OSC server for receiving from Ableton
            osc_dispatcher = dispatcher.Dispatcher()
            osc_dispatcher.map("/live/state", self._handle_osc_state_update)
            osc_dispatcher.map("/live/command_result", self._handle_osc_command_result)

            self.osc_server = osc_server.ThreadingOSCUDPServer(
                (self.osc_host, self.osc_server_port), osc_dispatcher
            )

            # Start OSC server in background thread
            self.osc_server_thread = threading.Thread(target=self.osc_server.serve_forever, daemon=True)
            self.osc_server_thread.start()

            print("✅ OSC communication initialized")

        except Exception as e:
            print(f"⚠️ OSC initialization failed: {e}")
            self.osc_enabled = False

    def _handle_osc_state_update(self, address, *args):
        """Handle OSC state update from Ableton"""
        try:
            if len(args) >= 1:
                state_data = args[0] if isinstance(args[0], dict) else {"raw": args}
                self.current_state = state_data
                self.last_ableton_update = time.time()
                print(f"📊 OSC State Update: {len(str(state_data))} chars")
        except Exception as e:
            print(f"⚠️ OSC state update error: {e}")

    def _handle_osc_command_result(self, address, *args):
        """Handle OSC command result from Ableton"""
        try:
            if len(args) >= 1:
                result = args[0] if isinstance(args[0], dict) else {"result": args}
                print(f"🎯 OSC Command Result: {result}")
        except Exception as e:
            print(f"⚠️ OSC command result error: {e}")

    def send_osc_command(self, command):
        """Send command via OSC to Ableton"""
        if not self.osc_enabled or not self.osc_client:
            return False

        try:
            # Convert command to OSC format
            osc_address = f"/live/command/{command.get('action', 'unknown')}"
            osc_args = [json.dumps(command)]
            self.osc_client.send_message(osc_address, osc_args)
            return True
        except Exception as e:
            print(f"⚠️ OSC send error: {e}")
            return False

    def stop(self):
        """Stop the server"""
        self.is_running = False

        # Stop OSC server
        if self.osc_server:
            self.osc_server.shutdown()

        if self.server_socket:
            self.server_socket.close()
        print("✅ Server stopped")
    
    def handle_client(self, client, address):
        """Handle client connection"""
        try:
            print(f"🔌 New connection from {address[0]}:{address[1]}")
            client.settimeout(5.0)  # Timeout for reads
            
            buffer = ""  # Buffer for partial messages
            
            client_type = None  # 'ableton' or 'gui'
            
            while self.is_running:
                try:
                    data = client.recv(8192).decode('utf-8')
                    if not data:
                        break
                        
                    buffer += data
                    
                    # Process complete messages (split by \n delimiter)
                    while '\n' in buffer:
                        message_str, buffer = buffer.split('\n', 1)
                        if not message_str.strip():
                            continue  # Skip empty messages
                        try:
                            message = json.loads(message_str)
                            msg_type = message.get('type')
                            
                            if msg_type == 'ping':
                                # Handle ping for connection monitoring (silent)
                                ableton_connected = (time.time() - self.last_ableton_update) < 10
                                response = {
                                    "status": "ok",
                                    "ableton_connected": ableton_connected,
                                    "message": "pong"
                                }
                                
                            elif msg_type == 'connect':
                                client_type = message.get('client')
                                print(f"✅ {client_type.upper()} connected")
                                
                                # Don't add GUI to broadcast list for command connections
                                # Command connections are short-lived and don't need broadcasts
                                
                                response = {"status": "ok", "message": "Connected"}
                                
                            elif msg_type == 'state_update' and client_type == 'ableton':
                                self.handle_state_update(message)
                                response = {"status": "ok", "message": "State updated"}
                                
                            elif msg_type == 'get_commands' and client_type == 'ableton':
                                response = self.get_pending_commands()
                                
                            elif msg_type == 'command' and client_type == 'gui':
                                response = self.handle_command(message)
                                
                            else:
                                response = {"error": f"Unknown message type: {msg_type} for client {client_type}"}
                            
                            # Send response
                            client.sendall(json.dumps(response).encode('utf-8') + b'\n')
                            
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON parse error: {e}")
                            print(f"   Received data: {message_str[:200]}")
                            # Don't clear entire buffer, just skip this message
                        
                except socket.timeout:
                    # Check if we have pending commands to send proactively (for Ableton)
                    if client_type == 'ableton' and self.command_queue:
                        commands_response = self.get_pending_commands()
                        client.sendall(json.dumps(commands_response).encode('utf-8') + b'\n')
                    continue
                    
                except Exception as e:
                    print(f"⚠️ Client read error: {e}")
                    break
            
        except Exception as e:
            print(f"⚠️ Client handler error: {e}")
        finally:
            # Remove GUI client from broadcast list
            if client_type == 'gui':
                with self.clients_lock:
                    self.gui_clients = [c for c in self.gui_clients if c['socket'] != client]
            
            client.close()
            if client_type:
                print(f"🔌 {client_type.upper()} disconnected")
            
    def log_message(self, message):
        """Helper to print messages with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def handle_state_update(self, message):
        """Handle Ableton state update"""
        self.current_state = message.get('data', {})
        self.last_ableton_update = time.time()  # Update timestamp
        num_tracks = len(self.current_state.get('tracks', []))
        tempo = self.current_state.get('tempo', 0)
        print(f"📊 State Update: {num_tracks} tracks, {tempo:.1f} BPM")
        
        # Broadcast state update to all connected GUI clients
        self.broadcast_to_gui_clients({
            "type": "state_update",
            "data": self.current_state
        })
    
    def broadcast_to_gui_clients(self, message):
        """Broadcast message to all connected GUI clients"""
        with self.clients_lock:
            disconnected = []
            for client_info in self.gui_clients:
                try:
                    client_info['socket'].sendall(json.dumps(message).encode('utf-8') + b'\n')
                except:
                    disconnected.append(client_info)
            
            # Remove disconnected clients
            for client_info in disconnected:
                self.gui_clients.remove(client_info)
                print(f"🔌 GUI client disconnected (cleanup)")
    
    def handle_command(self, message):
        """Handle AI command request"""
        prompt = message.get('prompt', '')
        
        if not prompt:
            return {"error": "No prompt provided"}
        
        print(f"💭 User: {prompt}")
        
        # Update provider and API key from message if provided
        provider = message.get('provider', self.llm.provider)
        api_key = message.get('api_key')
        
        # Temporarily update LLM provider and API key
        original_provider = self.llm.provider
        original_api_key = None
        
        if provider:
            self.llm.provider = provider.upper()
            print(f"🔄 Using provider: {self.llm.provider}")
        
        if api_key and provider:
            original_api_key = self.llm.api_keys.get(provider.upper())
            self.llm.api_keys[provider.upper()] = api_key
            print(f"🔑 Using API key from GUI for {provider.upper()}")
        
        # Call LLM
        result = self.llm.call_llm(prompt, self.current_state)
        
        # Restore original settings
        self.llm.provider = original_provider
        if original_api_key is not None and provider:
            self.llm.api_keys[provider.upper()] = original_api_key
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return {"error": result['error']}
        
        response_text = result.get('response', '')
        print(f"🤖 AI ({result.get('provider', 'Unknown')}): {response_text[:100]}...")
        
        # Add to history
        self.chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        self.chat_history.append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get commands - either from MCP tools or parse from text
        if 'commands' in result:
            # MCP tools already converted to commands
            commands = result['commands']
            print(f"🔧 Using {len(commands)} command(s) from MCP tools")
        else:
            # Parse commands from response text (for GROQ, GPT, etc.)
            commands = self.parse_commands(response_text)

        # Process and fix commands
        processed_commands = []
        track_created = False

        for cmd in commands:
            # Track if we created a track in this batch
            if cmd.get('action') in ['create_midi_track', 'create_audio_track']:
                track_created = True

            # Fix track_index for commands that reference the newly created track
            if cmd.get('action') in ['create_clip', 'add_notes'] and track_created:
                # If we created a track, this command should use the last track index
                current_tracks = len(self.current_state.get('tracks', []))
                # If we created a track, the new track will be at current_tracks index
                # (since the state update happens after command execution)
                cmd['parameters']['track_index'] = current_tracks
                print(f"🔧 Fixed track reference -> track_index: {current_tracks} for {cmd.get('action')}")

            processed_commands.append(cmd)

        # Send commands to Ableton (try OSC first, then socket)
        if processed_commands:
            osc_sent = 0
            socket_queued = 0

            print(f"🎯 Processing {len(processed_commands)} commands from LLM:")
            for i, cmd in enumerate(processed_commands):
                print(f"  {i+1}. {cmd.get('action', 'unknown')}: {cmd}")

                # Try OSC first
                if self.send_osc_command(cmd):
                    osc_sent += 1
                else:
                    # Fallback to socket communication
                    self.command_queue.append(cmd)
                    socket_queued += 1
                    print(f"    📨 Queued for socket: {cmd.get('action')}")

            if osc_sent > 0:
                print(f"✅ Sent {osc_sent} command(s) via OSC")
            if socket_queued > 0:
                print(f"📨 Queued {socket_queued} command(s) for socket communication")
                print(f"📊 Command queue length: {len(self.command_queue)}")
        
        return {
            "response": response_text,
            "commands": commands,
            "provider": result.get('provider')
        }
    
    def handle_voice_command(self, message):
        """Handle voice command"""
        if not self.voice:
            return {"error": "Voice controller not available - PyAudio not installed"}

        language = message.get('language', 'en')

        # Listen for voice input
        result = self.voice.listen(language)

        if 'error' in result:
            return result

        text = result.get('text', '')

        # Process as command
        command_response = self.handle_command({"prompt": text})

        # Speak response if available
        if 'response' in command_response:
            self.voice.speak(command_response['response'], language)

        return command_response
    
    def handle_query(self, message):
        """Handle information query"""
        query = message.get('query', '')
        
        if not query:
            return {"error": "No query provided"}
        
        # Call LLM for answer
        result = self.llm.call_llm(query, self.current_state)
        
        return result
    
    def parse_commands(self, text):
        """Parse JSON commands from LLM response"""
        commands = []

        # Method 1: Try to find JSON code blocks (markdown style)
        import re
        code_blocks = re.findall(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
        for block in code_blocks:
            try:
                cmd_list = json.loads(block)
                if isinstance(cmd_list, list):
                    for cmd in cmd_list:
                        if isinstance(cmd, dict) and 'action' in cmd:
                            commands.append(cmd)
                            print(f"✅ Parsed command from array code block: {cmd.get('action')}")
            except Exception as e:
                pass

        # Method 2: Try to find JSON arrays (markdown style)
        code_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        for block in code_blocks:
            try:
                cmd = json.loads(block)
                if 'action' in cmd:
                    commands.append(cmd)
                    print(f"✅ Parsed command from object code block: {cmd.get('action')}")
            except Exception as e:
                pass

        # Method 3: Try to parse standalone JSON arrays
        # Find all top-level [ ] pairs
        bracket_count = 0
        start_idx = -1

        for i, char in enumerate(text):
            if char == '[':
                if bracket_count == 0:
                    start_idx = i
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0 and start_idx != -1:
                    # Found complete JSON array
                    json_str = text[start_idx:i+1]
                    try:
                        cmd_list = json.loads(json_str)
                        if isinstance(cmd_list, list):
                            for cmd in cmd_list:
                                if isinstance(cmd, dict) and 'action' in cmd and cmd not in commands:
                                    commands.append(cmd)
                                    print(f"✅ Parsed command from array: {cmd.get('action')}")
                    except Exception as e:
                        pass
                    start_idx = -1

        # Method 4: Try to parse standalone JSON objects (with nested braces)
        # Find all top-level { } pairs
        brace_count = 0
        start_idx = -1

        for i, char in enumerate(text):
            if char == '{':
                if brace_count == 0:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    # Found complete JSON object
                    json_str = text[start_idx:i+1]
                    try:
                        cmd = json.loads(json_str)
                        if 'action' in cmd and cmd not in commands:
                            commands.append(cmd)
                            print(f"✅ Parsed command from object: {cmd.get('action')}")
                    except Exception as e:
                        pass
                    start_idx = -1

        return commands

    def get_pending_commands(self):
        """Get and clear pending commands"""
        if self.command_queue:
            commands = self.command_queue.copy()
            self.command_queue.clear()
            print(f"📤 Sending {len(commands)} command(s) via persistent connection")
            return {
                "type": "commands",
                "status": "ok",
                "commands": commands
            }
        else:
            return {
                "type": "commands",
                "status": "ok",
                "commands": []
            }


def main():
    """Main entry point"""
    import sys

    # Let AIConfig auto-detect by default (robust vs working directory)
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    server = AICopilotServer(config_path=config_path)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


