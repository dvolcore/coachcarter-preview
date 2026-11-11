#!/bin/bash
# Restore Coach's private photos: orient, crop to the print, remove screen moire, level, sharpen. No generative edits.
set -e
S="$1"; O="$2"; mkdir -p "$O"; cd "$S/raw"
FIN="-strip -interlace Plane -quality 86"
SCR="-colorspace Lab -channel 1,2 -gaussian-blur 0x7 +channel -colorspace sRGB -gaussian-blur 0x0.9"
# courtside-prince-jackson.jpg is the AI-upscaled version Ralph chose on 2026-11-10 (tracking/private_collection/upscale_test); do not regenerate it here.
: # magick IMG_2272.jpg -filter Lanczos -resize 1500x -unsharp 0x1.4+0.7+0.02 -contrast-stretch 0.3%x0.3% $FIN "$O/courtside-prince-jackson.jpg"
magick IMG_2266.jpg -filter Lanczos -resize 1500x -unsharp 0x1.4+0.7+0.02 -contrast-stretch 0.3%x0.3% $FIN "$O/courtside-prince-jackson-2.jpg"
magick IMG_9294.jpg -crop 1085x728+10+10 +repage $SCR -filter Lanczos -resize 1500x -unsharp 0x1.2+0.6+0.02 -contrast-stretch 0.4%x0.6% -modulate 100,92 $FIN "$O/with-usher.jpg"
magick Ken-Sam-Phil.jpg -unsharp 0x0.8+0.4+0.02 $FIN "$O/drphil-jackson.jpg"
magick Ken-Sam-Phil2.jpg -unsharp 0x0.8+0.4+0.02 $FIN "$O/drphil-set.jpg"
magick IMG_4740.jpg -colorspace Gray -contrast-stretch 0.5%x0.5% -resize 1500x1800 -unsharp 0x0.8+0.5+0.02 $FIN "$O/all-stars-24.jpg"
magick IMG_3231.jpg -auto-orient -colorspace Gray -contrast-stretch 0.6%x0.6% -resize 1800x -unsharp 0x0.8+0.5+0.02 $FIN "$O/oilers-team.jpg"
magick IMG_3232.jpg -auto-orient -contrast-stretch 0.6%x0.6% -resize 1800x -unsharp 0x0.8+0.5+0.02 $FIN "$O/huddle.jpg"
magick IMG_8198.jpg -auto-orient -contrast-stretch 0.4%x0.4% -resize 1800x -unsharp 0x0.8+0.5+0.02 $FIN "$O/team-jackets.jpg"
magick IMG_3242.jpg -auto-orient -crop 1300x1560+0+104 +repage -contrast-stretch 0.4%x0.4% -unsharp 0x0.8+0.5+0.02 $FIN "$O/on-the-floor.jpg"
magick IMG_3237.jpg -auto-orient -crop 2238x3690+0+330 +repage -contrast-stretch 0.5%x0.5% -resize 1400x1800 -unsharp 0x0.8+0.5+0.02 $FIN "$O/by-the-trailer.jpg"
magick IMG_3257.jpg -auto-orient -crop 2820x2230+356+454 +repage -rotate 180 -contrast-stretch 0.5%x0.5% -resize 1800x -unsharp 0x0.8+0.5+0.02 $FIN "$O/on-location.jpg"
magick IMG_3250.jpg -auto-orient -contrast-stretch 0.3%x0.3% -resize 1800x -unsharp 0x0.8+0.4+0.02 $FIN "$O/portrait-pair.jpg"
magick IMG_8705.jpg -auto-orient -resize 1400x1800 -unsharp 0x0.8+0.4+0.02 $FIN "$O/handshake.jpg"
magick IMG_2448_2.jpg -auto-orient -resize 1400x1800 -unsharp 0x0.8+0.4+0.02 $FIN "$O/coach-portrait.jpg"
magick 151_5156.jpg -colorspace sRGB -resize 2000x -unsharp 0x0.8+0.4+0.02 $FIN "$O/in-the-hallway.jpg"
magick IMG_8432.jpg -filter Lanczos -resize 1100x -unsharp 0x1+0.5+0.02 $FIN "$O/in-the-gym.jpg"
magick IMG_6606.jpg -crop 3000x2100+130+300 +repage $SCR -resize 1600x -unsharp 0x1.2+0.6+0.02 -contrast-stretch 0.5%x0.5% $FIN "$O/three-men.jpg"
magick IMG_5374.jpg $SCR -resize 1600x -unsharp 0x1.2+0.6+0.02 -contrast-stretch 0.5%x0.5% $FIN "$O/five-men.jpg"
magick IMG_7448.jpg -crop 881x1455+0+30 +repage -filter Lanczos -resize 1100x -unsharp 0x1.2+0.6+0.02 $FIN "$O/on-set.jpg"
cd "$O"; for f in *.jpg; do case "$f" in *-900.jpg) continue;; esac; magick "$f" -resize "900x900>" $FIN -quality 80 "${f%.jpg}-900.jpg"; done
for f in *.jpg; do echo "$f $(magick "$f" -format '%wx%h' info:) $(( $(stat -f %z "$f") / 1024 ))K"; done
montage *.jpg -tile 5x -geometry 380x380+4+4 -background '#111' "$S/out_sheet.jpg" 2>/dev/null
du -sh "$O"
