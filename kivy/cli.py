#!/usr/bin/env python3
"""
Image to Sketch Animation - CLI Mode
Command-line interface for batch processing without GUI
"""

import os
import sys

# Disable Kivy's argument parser before any Kivy imports
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '1'  # Disable console logging

import argparse
from pathlib import Path

# Import only the sketch API, not the GUI
from sketchApi import initiate_sketch

# Determine platform
if sys.platform.startswith('win'):
    platform = 'win'
elif sys.platform.startswith('darwin'):
    platform = 'macosx'
elif sys.platform.startswith('linux'):
    platform = 'linux'
else:
    platform = 'unknown'

def run_cli(args):
    """Run the application in CLI mode without GUI"""
    
    # Validate input path
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: Input path '{args.input}' does not exist")
        sys.exit(1)
    
    # Determine if it's a folder or single image
    is_folder = input_path.is_dir()
    
    # Set output directory
    output_dir = args.output if args.output else os.path.join(os.getcwd(), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Get valid split lengths for the first image
    if is_folder:
        img_extensions = [".png", ".jpg", ".jpeg", ".webp"]
        img_files = [f for f in os.listdir(str(input_path)) 
                     if os.path.splitext(f)[1].lower() in img_extensions]
        if not img_files:
            print("❌ No image files found in the folder")
            sys.exit(1)
        first_image = os.path.join(str(input_path), img_files[0])
    else:
        first_image = str(input_path)
    
    # Get available split lengths from the image
    from sketchApi import get_split_lens
    split_info = get_split_lens(first_image)
    available_splits = split_info.get('split_lens', [])
    
    if not available_splits:
        print(f"❌ Error: Could not determine valid split lengths for image")
        sys.exit(1)
    
    # Auto-select best split_len from the range
    split_len_min = None
    split_len_max = None
    
    # Parse range if provided
    if hasattr(args, 'split_len_range') and args.split_len_range:
        try:
            parts = args.split_len_range.split('-')
            if len(parts) == 2:
                split_len_min = int(parts[0])
                split_len_max = int(parts[1])
            else:
                print(f"⚠️  Invalid range format: {args.split_len_range}. Use format: 'min-max' (e.g., '10-40')")
                split_len_min = None
                split_len_max = None
        except ValueError:
            print(f"⚠️  Invalid range values: {args.split_len_range}. Using auto-selection.")
    
    if split_len_min and split_len_max:
        # User provided a range - pick SMALLEST value in range (closest to min)
        selected_split = None
        for split in sorted(available_splits):  # Try smaller values first
            if split_len_min <= split <= split_len_max:
                selected_split = split
                break
        
        if not selected_split:
            # If no match in range, use the closest available to the minimum
            selected_split = min(available_splits, key=lambda x: abs(x - split_len_min))
            print(f"⚠️  No split length in range [{split_len_min}-{split_len_max}] available")
            print(f"   Using closest to {split_len_min}: {selected_split}")
    elif hasattr(args, 'split_len') and args.split_len:
        # User provided a specific value
        if args.split_len in available_splits:
            selected_split = args.split_len
        else:
            # Find closest available
            selected_split = min(available_splits, key=lambda x: abs(x - args.split_len))
            print(f"⚠️  Split length {args.split_len} not available for this image")
            print(f"   Using closest available: {selected_split}")
    else:
        # No preference, use a good default (prefer values around 10-20)
        preferred = [20, 10, 40, 8, 16, 32, 4]
        selected_split = None
        for pref in preferred:
            if pref in available_splits:
                selected_split = pref
                break
        if not selected_split:
            selected_split = available_splits[len(available_splits)//2]  # Middle value
    
    print(f"🎨 Image to Sketch Animation - CLI Mode")
    print(f"📁 Input: {input_path}")
    print(f"📂 Output: {output_dir}")
    print(f"⚙️  Mode: {'Batch (Folder)' if is_folder else 'Single Image'}")
    print(f"📐 Image Info: {split_info.get('image_res', 'Unknown')}")
    print(f"📊 Available Split Lengths: {sorted(available_splits, reverse=True)}")
    print(f"✅ Selected Split Length: {selected_split}")
    print(f"🎬 Frame Rate: {args.frame_rate}")
    print(f"⏭️  Object Skip: {args.obj_skip}")
    print(f"⏭️  Background Skip: {args.bck_skip}")
    print(f"⏱️  Main Image Duration: {args.duration}s")
    print(f"🎨 Draw Color: {'Yes' if args.draw_color else 'No'}")
    print(f"🔄 Two Pass: {'Yes' if args.two_pass else 'No'}")
    print(f"🚀 Fill Speed: {args.fill_speed}x")
    print(f"🎞️  H264 Convert: {'Yes' if args.h264 else 'No'}")
    if args.element_mode:
        print(f"🧩 Element Mode: Yes")
        print(f"   ├─ White Gap: {args.white_gap}px")
        print(f"   └─ Sort Direction: {args.sort_direction}")
    print("-" * 50)
    
    # Callback for completion
    def cli_callback(success, message):
        if success:
            print(f"✅ Success: {message}")
        else:
            print(f"❌ Error: {message}")
    
    if is_folder:
        # Batch processing
        print(f"📊 Found {len(img_files)} images to process\n")
        
        for idx, img_file in enumerate(img_files, 1):
            full_path = os.path.join(str(input_path), img_file)
            print(f"[{idx}/{len(img_files)}] Processing: {img_file}")
            
            initiate_sketch(
                full_path,
                selected_split,
                args.frame_rate,
                args.obj_skip,
                args.bck_skip,
                args.duration,
                cli_callback,
                output_dir,
                platform,
                args.end_color,
                args.draw_color,
                args.two_pass,
                args.h264,
                args.fill_speed,
                args.element_mode,
                args.white_gap,
                args.sort_direction,
                None  # No progress callback in CLI mode
            )
            print()  # Empty line between files
    else:
        # Single image processing
        print(f"🎬 Processing single image...\n")
        initiate_sketch(
            str(input_path),
            selected_split,
            args.frame_rate,
            args.obj_skip,
            args.bck_skip,
            args.duration,
            cli_callback,
            output_dir,
            platform,
            args.end_color,
            args.draw_color,
            args.two_pass,
            args.h264,
            args.fill_speed,
            args.element_mode,
            args.white_gap,
            args.sort_direction,
            None  # No progress callback in CLI mode
        )
    
    print("\n✨ All processing complete!")

def main():
    try:
        # Create argument parser
        parser = argparse.ArgumentParser(
            description='Image to Sketch Animation - Convert images to sketch-style animations',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  # Single image with default settings
  python cli.py --input photo.jpg
  
  # Batch process folder with custom settings
  python cli.py --input ./images --output ./videos --frame-rate 30 --two-pass
  
  # Full custom configuration
  python cli.py -i image.png -o ./output -fr 24 -os 3 -bs 5 -d 2 -dc -tp -fs 8 -h264
        '''
        )
        
        # Required arguments
        parser.add_argument('-i', '--input', type=str, required=True,
                            help='Input image file or folder path (required)')
        
        # Optional arguments
        parser.add_argument('-o', '--output', type=str,
                            help='Output directory (default: ./output)')
        
        # Split length - can be single value or range
        split_group = parser.add_mutually_exclusive_group()
        split_group.add_argument('-sl', '--split-len', type=int,
                            help='Split length for processing (auto-selected from available if not valid)')
        split_group.add_argument('-slr', '--split-len-range', type=str,
                            help='Split length range (e.g., "10-40" will pick best available in range)')
        
        parser.add_argument('-fr', '--frame-rate', type=int, default=24,
                            help='Video frame rate (default: 24)')
        
        parser.add_argument('-os', '--obj-skip', type=int, default=2,
                            help='Object skip rate (default: 2)')
        
        parser.add_argument('-bs', '--bck-skip', type=int, default=3,
                            help='Background skip rate (default: 3)')
        
        parser.add_argument('-d', '--duration', type=int, default=1,
                            help='Main image display duration in seconds (default: 1)')
        
        parser.add_argument('-dc', '--draw-color', action='store_true',
                            help='Draw with color from the start')
        
        parser.add_argument('-tp', '--two-pass', action='store_true',
                            help='Use two-pass rendering (lines then fill)')
        
        parser.add_argument('-fs', '--fill-speed', type=int, default=5,
                            help='Fill speed multiplier (default: 5)')
        
        parser.add_argument('-em', '--element-mode', action='store_true',
                            help='Detect and draw each element separately (for images with white background)')
        
        parser.add_argument('-wg', '--white-gap', type=int, default=10,
                            help='White gap threshold between elements in pixels (default: 10)')
        
        parser.add_argument('-sd', '--sort-direction', type=str, default='right-top',
                            choices=['right-top', 'right-bottom', 'left-top', 'left-bottom'],
                            help='Element drawing order (default: right-top)')
        
        parser.add_argument('-h264', '--h264', action='store_true',
                            help='Convert to H264 format after generation')
        
        parser.add_argument('-ec', '--end-color', action='store_true', default=True,
                            help='Show colored image at the end (default: True)')
        
        # Parse arguments
        args = parser.parse_args()
        
        # Run CLI mode
        run_cli(args)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal Error: {str(e)}")
        import traceback
        print("\n📋 Full error details:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
