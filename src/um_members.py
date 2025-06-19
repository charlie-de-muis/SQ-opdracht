#!/usr/bin/env python3

import sys
import os
from urban_mobility_system import UrbanMobilitySystem

def main():
    """Main entry point for the Urban Mobility Backend System"""
    print("=" * 60)
    print("    URBAN MOBILITY BACKEND SYSTEM")
    print("    Secure Management Console")
    print("=" * 60)
    print()
    
    try:
        # Initialize the system
        system = UrbanMobilitySystem()
        
        # Start the main application loop
        system.run()
        
    except KeyboardInterrupt:
        print("\n\nSystem shutdown requested by user.")
        print("Thank you for using Urban Mobility Backend System!")
        
    except Exception as e:
        print(f"\nCritical system error: {e}")
        print("Please contact system administrator.")
        sys.exit(1)

if __name__ == "__main__":
    main()
