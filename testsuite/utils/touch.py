#!/usr/bin/env python3
"""
EVEMU Virtual Touch Device - Melfas LGDisplay Incell Touch
Exact virtual copy based on evemu data from Raspberry Pi

This script creates a virtual input device that mimics the exact specifications
and behavior of the original touch device.
"""

import os
import sys
import time
import struct
import threading
from pathlib import Path

try:
    import evdev
    from evdev import UInput, InputDevice, ecodes, list_devices
except ImportError:
    print("Error: python-evdev not installed. Install with: pip install evdev")
    sys.exit(1)

class MelfasTouchDevice:
    """Virtual Melfas LGDisplay Incell Touch Device"""
    
    # Device specifications from evemu data
    DEVICE_NAME = "Melfas LGDisplay Incell Touch"
    VENDOR_ID = 0x1fd2
    PRODUCT_ID = 0x8105
    VERSION = 0x111
    BUS_TYPE = 0x03  # USB
    
    # Physical dimensions
    PHYSICAL_WIDTH_MM = 526
    PHYSICAL_HEIGHT_MM = 292
    
    # Coordinate ranges
    ABS_X_MIN = 0
    ABS_X_MAX = 1079
    ABS_Y_MIN = 0
    ABS_Y_MAX = 1919
    
    # Multi-touch specifications
    MT_SLOT_MIN = 0
    MT_SLOT_MAX = 9
    MT_TRACKING_ID_MIN = 0
    MT_TRACKING_ID_MAX = 65535
    
    # Resolution (units per mm)
    X_RESOLUTION = 2.05
    Y_RESOLUTION = 6.49
    
    def __init__(self):
        self.device = None
        self.current_tracking_id = 0
        self.active_slots = {}
        self.is_running = False
        
    def create_device_capabilities(self):
        """Create device capabilities matching the evemu specification"""
        
        # AbsInfo: (min, max, fuzz, flat, resolution)
        capabilities = {
            # EV_KEY events
            ecodes.EV_KEY: [
                ecodes.BTN_TOUCH
            ],
            
            # EV_ABS events with their ranges and resolutions
            ecodes.EV_ABS: [
                # Single touch coordinates
                (ecodes.ABS_X, evdev.AbsInfo(
                    value=0, min=self.ABS_X_MIN, max=self.ABS_X_MAX, 
                    fuzz=0, flat=0, resolution=self.X_RESOLUTION)),
                (ecodes.ABS_Y, evdev.AbsInfo(
                    value=0, min=self.ABS_Y_MIN, max=self.ABS_Y_MAX, 
                    fuzz=0, flat=0, resolution=self.Y_RESOLUTION)),
                
                # Multi-touch slot
                (ecodes.ABS_MT_SLOT, evdev.AbsInfo(
                    value=0, min=self.MT_SLOT_MIN, max=self.MT_SLOT_MAX, 
                    fuzz=0, flat=0, resolution=0)),
                
                # Multi-touch coordinates
                (ecodes.ABS_MT_POSITION_X, evdev.AbsInfo(
                    value=0, min=self.ABS_X_MIN, max=self.ABS_X_MAX, 
                    fuzz=0, flat=0, resolution=self.X_RESOLUTION)),
                (ecodes.ABS_MT_POSITION_Y, evdev.AbsInfo(
                    value=0, min=self.ABS_Y_MIN, max=self.ABS_Y_MAX, 
                    fuzz=0, flat=0, resolution=self.Y_RESOLUTION)),
                
                # Multi-touch tracking ID
                (ecodes.ABS_MT_TRACKING_ID, evdev.AbsInfo(
                    value=0, min=self.MT_TRACKING_ID_MIN, max=self.MT_TRACKING_ID_MAX, 
                    fuzz=0, flat=0, resolution=0))
            ]
        }
        
        return capabilities
    
    def create_virtual_device(self):
        """Create the virtual input device"""
        try:
            capabilities = self.create_device_capabilities()
            
            # Create device info
            device_info = evdev.DeviceInfo(
                bustype=self.BUS_TYPE,
                vendor=self.VENDOR_ID,
                product=self.PRODUCT_ID,
                version=self.VERSION
            )
            
            # Create UInput device with exact specifications
            self.device = UInput(
                events=capabilities,
                name=self.DEVICE_NAME,
                devinfo=device_info
            )
            
            print(f"✓ Created virtual device: {self.DEVICE_NAME}")
            print(f"  Vendor: 0x{self.VENDOR_ID:04x}")
            print(f"  Product: 0x{self.PRODUCT_ID:04x}")
            print(f"  Version: 0x{self.VERSION:04x}")
            print(f"  Physical size: {self.PHYSICAL_WIDTH_MM}x{self.PHYSICAL_HEIGHT_MM}mm")
            print(f"  Coordinate range: {self.ABS_X_MAX}x{self.ABS_Y_MAX}")
            print(f"  Multi-touch slots: {self.MT_SLOT_MAX + 1}")
            print(f"  Device path: {self.device.device.path}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to create virtual device: {e}")
            print("Trying with minimal capabilities...")
            
            # Fallback with minimal capabilities
            try:
                minimal_caps = {
                    ecodes.EV_KEY: [ecodes.BTN_TOUCH],
                    ecodes.EV_ABS: [
                        (ecodes.ABS_X, evdev.AbsInfo(0, 0, 4095, 0, 0, 8)),
                        (ecodes.ABS_Y, evdev.AbsInfo(0, 0, 4095, 0, 0, 14)),
                        (ecodes.ABS_MT_POSITION_X, evdev.AbsInfo(0, 0, 4095, 0, 0, 8)),
                        (ecodes.ABS_MT_POSITION_Y, evdev.AbsInfo(0, 0, 4095, 0, 0, 14)),
                        (ecodes.ABS_MT_SLOT, evdev.AbsInfo(0, 0, 9, 0, 0, 0)),
                        (ecodes.ABS_MT_TRACKING_ID, evdev.AbsInfo(0, 0, 65535, 0, 0, 0))
                    ]
                }
                
                self.device = UInput(
                    events=minimal_caps,
                    name=self.DEVICE_NAME
                )
                
                print(f"✓ Created virtual device with minimal capabilities")
                print(f"  Device path: {self.device.device.path}")
                return True
                
            except Exception as e2:
                print(f"✗ Failed with minimal capabilities too: {e2}")
                return False
    
    def log_event(self, event_type, event_code, value, timestamp=None):
        """Log an event in evemu format - removed for daemon mode"""
        pass
    
    def send_touch_down(self, x, y, slot=0):
        """Send touch down event"""
        tracking_id = self.current_tracking_id
        self.current_tracking_id += 1
        self.active_slots[slot] = tracking_id
        
        timestamp = int(time.time() * 1000000) % 100000  # Microsecond timestamp
        
        # Multi-touch events
        self.device.write(ecodes.EV_ABS, ecodes.ABS_MT_SLOT, slot)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_MT_TRACKING_ID, tracking_id)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_MT_POSITION_X, x)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_MT_POSITION_Y, y)
        
        # Single touch events
        self.device.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 1)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_X, x)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_Y, y)
        
        # Sync
        self.device.syn()
    
    def send_touch_move(self, x, y, slot=0):
        """Send touch move event"""
        if slot not in self.active_slots:
            return
        
        # Multi-touch position update
        self.device.write(ecodes.EV_ABS, ecodes.ABS_MT_POSITION_X, x)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_MT_POSITION_Y, y)
        
        # Single touch position update
        self.device.write(ecodes.EV_ABS, ecodes.ABS_X, x)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_Y, y)
        
        # Sync
        self.device.syn()
    
    def send_touch_up(self, slot=0):
        """Send touch up event"""
        if slot not in self.active_slots:
            return
        
        # End multi-touch tracking
        self.device.write(ecodes.EV_ABS, ecodes.ABS_MT_TRACKING_ID, -1)
        
        # Release touch
        self.device.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 0)
        
        # Sync
        self.device.syn()
        
        # Remove from active slots
        del self.active_slots[slot]
    
    def replay_original_events(self):
        """Replay the original touch events from evemu data"""
        print("\n--- Replaying original touch events ---")
        
        # First touch sequence (from evemu data)
        print("Touch 1: Down at (553, 1048)")
        self.send_touch_down(553, 1048)
        time.sleep(0.033)
        
        print("Touch 1: Move to (557, 1059)")
        self.send_touch_move(557, 1059)
        time.sleep(0.035)
        time.sleep(0.017)
        
        print("Touch 1: Up")
        self.send_touch_up()
        time.sleep(3.065)
        
        # Second touch sequence
        print("Touch 2: Down at (2330, 1908)")
        self.send_touch_down(2330, 1908)
        time.sleep(0.017)
        
        print("Touch 2: Move to (2329, 1907)")
        self.send_touch_move(2329, 1907)
        time.sleep(0.016)
        time.sleep(0.017)
        time.sleep(0.017)
        time.sleep(0.018)
        time.sleep(0.016)
        
        print("Touch 2: Up")
        self.send_touch_up()
        time.sleep(0.766)
        
        # Third touch sequence
        print("Touch 3: Down at (1956, 660)")
        self.send_touch_down(1956, 660)
        
        print("--- Original events replay complete ---\n")
    
    def run_daemon(self):
        """Run as daemon, waiting for external touch input"""
        print(f"\n✓ Virtual touch device daemon started")
        print(f"  Device: {self.DEVICE_NAME}")
        print(f"  Path: {self.device.device.path}")
        print(f"  PID: {os.getpid()}")
        print(f"  Coordinate range: 0-{self.ABS_X_MAX} x 0-{self.ABS_Y_MAX}")
        print(f"  Multi-touch slots: {self.MT_SLOT_MAX + 1}")
        print()
        print("Device is ready to receive touch events from external sources.")
        print("Press Ctrl+C to stop the daemon.")
        print()
        
        # Keep the device alive
        while self.is_running:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nReceived interrupt signal, shutting down...")
                break
            except Exception as e:
                print(f"Error in daemon loop: {e}")
                time.sleep(1)
    
    def show_device_info(self):
        """Show device information"""
        print(f"\n=== Device Information ===")
        print(f"Name: {self.DEVICE_NAME}")
        print(f"Vendor ID: 0x{self.VENDOR_ID:04x}")
        print(f"Product ID: 0x{self.PRODUCT_ID:04x}")
        print(f"Version: 0x{self.VERSION:04x}")
        print(f"Bus Type: 0x{self.BUS_TYPE:04x}")
        print(f"Physical Size: {self.PHYSICAL_WIDTH_MM}x{self.PHYSICAL_HEIGHT_MM}mm")
        print(f"Coordinate Range: {self.ABS_X_MAX}x{self.ABS_Y_MAX}")
        print(f"Resolution: {self.X_RESOLUTION}x{self.Y_RESOLUTION} units/mm")
        print(f"Multi-touch Slots: {self.MT_SLOT_MAX + 1}")
        print(f"Active Slots: {list(self.active_slots.keys())}")
        if self.device:
            print(f"Device Path: {self.device.device.path}")
        print()
    
    def start(self):
        """Start the virtual device"""
        print("EVEMU Virtual Touch Device - Melfas LGDisplay Incell Touch")
        print("=" * 60)
        
        if not self.create_virtual_device():
            return False
        
        self.is_running = True
        
        print(f"\n✓ Virtual device ready!")
        print(f"  Device can be found at: {self.device.device.path}")
        print(f"  Test with: evtest {self.device.device.path}")
        print(f"  Or use: cat {self.device.device.path}")
        
        return True
    
    def stop(self):
        """Stop the virtual device"""
        self.is_running = False
        if self.device:
            self.device.close()
            print("✓ Virtual device closed")
    
    def stop(self):
        """Stop the virtual device"""
        self.is_running = False
        if self.device:
            self.device.close()
            print("✓ Virtual device closed")
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Error: This script requires root privileges to create virtual input devices")
        print("Run with: sudo python3 evemu_touch_device.py")
        sys.exit(1)
    
    device = MelfasTouchDevice()
    
    try:
        if device.start():
            device.run_daemon()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        device.stop()


