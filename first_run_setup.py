"""
Profesor Abelton - First Run Setup
Automatically installs RemoteScript to Ableton User Library
Version: 2.0.0
"""

import os
import sys
import shutil
from pathlib import Path
import platform


def get_ableton_user_library():
    """Detect Ableton User Library location"""
    system = platform.system()
    
    if system == "Windows":
        # Windows: Documents\Ableton\User Library
        documents = Path.home() / "Documents"
        ableton_path = documents / "Ableton" / "User Library" / "Remote Scripts"
        
    elif system == "Darwin":  # macOS
        # macOS: ~/Music/Ableton/User Library
        ableton_path = Path.home() / "Music" / "Ableton" / "User Library" / "Remote Scripts"
        
    else:  # Linux
        # Linux: ~/Documents/Ableton/User Library (or custom)
        documents = Path.home() / "Documents"
        ableton_path = documents / "Ableton" / "User Library" / "Remote Scripts"
    
    return ableton_path


def find_ableton_versions():
    """Find all installed Ableton versions"""
    system = platform.system()
    versions = []
    
    if system == "Windows":
        # Check common Ableton installation paths
        program_data = Path("C:/ProgramData/Ableton")
        if program_data.exists():
            for item in program_data.iterdir():
                if item.is_dir() and "Live" in item.name:
                    versions.append(item.name)
    
    elif system == "Darwin":
        # macOS
        app_path = Path("/Applications")
        for item in app_path.glob("Ableton Live*.app"):
            versions.append(item.stem)
    
    return versions


def check_if_installed():
    """Check if RemoteScript is already installed"""
    ableton_scripts = get_ableton_user_library()
    ai_copilot_path = ableton_scripts / "ProfesorAbelton"
    
    if ai_copilot_path.exists() and (ai_copilot_path / "__init__.py").exists():
        return True
    return False


def install_remote_script():
    """Install RemoteScript to Ableton User Library"""
    print("\n" + "=" * 60)
    print("  🎓 PROFESOR ABELTON - FIRST RUN SETUP")
    print("=" * 60)
    print()
    
    # Check if already installed
    if check_if_installed():
        print("✅ RemoteScript already installed!")
        print()
        return True
    
    print("📦 Installing Ableton RemoteScript...")
    print()
    
    # Get source RemoteScript
    if getattr(sys, 'frozen', False):
        # Running as .exe
        base_path = Path(sys._MEIPASS)
    else:
        # Running as Python script
        base_path = Path(__file__).parent
    
    source_script = base_path / "RemoteScript"
    
    if not source_script.exists():
        print("❌ Error: RemoteScript folder not found!")
        print(f"   Looking for: {source_script}")
        print()
        return False
    
    # Get destination path
    ableton_scripts = get_ableton_user_library()
    destination = ableton_scripts / "ProfesorAbelton"
    
    # Check Ableton versions
    versions = find_ableton_versions()
    if versions:
        print(f"🎹 Detected Ableton: {', '.join(versions)}")
    else:
        print("⚠️  No Ableton installation detected")
        print("   (This is OK if Ableton is installed elsewhere)")
    print()
    
    # Create directories if needed
    try:
        ableton_scripts.mkdir(parents=True, exist_ok=True)
        print(f"📁 Target directory: {ableton_scripts}")
        print()
        
        # Copy RemoteScript
        if destination.exists():
            print("🗑️  Removing old installation...")
            shutil.rmtree(destination)
        
        print("📋 Copying RemoteScript files...")
        shutil.copytree(source_script, destination)
        
        # Verify installation
        if (destination / "__init__.py").exists():
            print()
            print("✅ RemoteScript installed successfully!")
            print()
            print("=" * 60)
            print("  NEXT STEPS:")
            print("=" * 60)
            print()
            print("1. Open Ableton Live")
            print("2. Go to Preferences (Ctrl+, or Cmd+,)")
            print("3. Select 'Link/Tempo/MIDI' tab")
            print("4. Under 'Control Surface', select: ProfesorAbelton")
            print("5. Leave Input and Output as: None")
            print("6. Close Preferences")
            print("7. Restart Ableton Live")
            print()
            print("✅ Setup complete! Profesor Abelton is ready!")
            print()
            print("=" * 60)
            print()
            
            return True
        else:
            print("❌ Installation verification failed!")
            return False
            
    except PermissionError:
        print()
        print("❌ Permission Error!")
        print("   Please run as Administrator (Windows) or with sudo (Mac/Linux)")
        print()
        return False
        
    except Exception as e:
        print()
        print(f"❌ Installation Error: {e}")
        print()
        return False


def manual_install_instructions():
    """Show manual installation instructions"""
    print("\n" + "=" * 60)
    print("  📖 MANUAL INSTALLATION")
    print("=" * 60)
    print()
    print("If automatic installation failed, follow these steps:")
    print()
    print("1. Locate the RemoteScript folder:")
    print("   (It's in the same folder as ProfesorAbleton.exe)")
    print()
    print("2. Copy the entire 'RemoteScript' folder")
    print()
    print("3. Navigate to your Ableton User Library:")
    
    system = platform.system()
    if system == "Windows":
        print("   C:\\Users\\[YourUsername]\\Documents\\Ableton\\User Library\\Remote Scripts\\")
    elif system == "Darwin":
        print("   ~/Music/Ableton/User Library/Remote Scripts/")
    else:
        print("   ~/Documents/Ableton/User Library/Remote Scripts/")
    
    print()
    print("4. Rename the copied folder to: ProfesorAbelton")
    print()
    print("5. Restart Ableton Live")
    print()
    print("6. Set up in Ableton Preferences:")
    print("   Control Surface: ProfesorAbelton")
    print("   Input: None")
    print("   Output: None")
    print()
    print("=" * 60)
    print()


def check_and_install():
    """Check if this is first run and install if needed"""
    # Check if RemoteScript is installed
    if check_if_installed():
        return True  # Already installed, continue normally
    
    # First run - install RemoteScript
    success = install_remote_script()
    
    if not success:
        # Show manual instructions
        response = input("Show manual installation instructions? (y/n): ")
        if response.lower() == 'y':
            manual_install_instructions()
    
    return success


if __name__ == "__main__":
    # Can be run standalone for testing
    check_and_install()
    input("\nPress Enter to continue...")

