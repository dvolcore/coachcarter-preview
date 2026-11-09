#!/bin/zsh
# Builds web video loops for the Coach Carter platform from Studio405 CC2 masters.
set -e
T=/Users/ralphd/Desktop/CC2_UPLOAD/CoachCarterII_Trailer_2026-10-22_1080p.mp4
R="/Users/ralphd/Downloads/Coach Carter II The Real Coach Carter.mov"
O=/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/site/assets/video
V="-c:v libx264 -preset slow -pix_fmt yuv420p -movflags +faststart -an"
seg(){ # out src start dur
  ffmpeg -v error -y -ss $3 -t $4 -i "$2" -vf "scale=1600:-2,fps=24" $=V -crf 24 "$5" ; }
mkdir -p $O/tmp
seg x "$T" 25.95 1.0 $O/tmp/a.mp4
seg x "$T" 26.95 1.05 $O/tmp/b.mp4
seg x "$R" 115.0 1.8 $O/tmp/c.mp4
seg x "$R" 118.0 1.6 $O/tmp/d.mp4
seg x "$R" 120.8 1.5 $O/tmp/e.mp4
seg x "$R" 128.4 1.6 $O/tmp/f.mp4
seg x "$T" 226.0 1.8 $O/tmp/g.mp4
seg x "$T" 214.2 1.6 $O/tmp/h.mp4
seg x "$T" 31.5 2.4 $O/tmp/i.mp4
printf "file '%s'\n" $O/tmp/{a,b,c,d,e,f,g,h,i}.mp4 > $O/tmp/list.txt
ffmpeg -v error -y -f concat -safe 0 -i $O/tmp/list.txt -c copy $O/hero_reel.mp4
loop(){ ffmpeg -v error -y -ss $2 -t $3 -i "$1" -vf "scale=1280:-2,fps=24" $=V -crf 26 $O/$4.mp4; ffmpeg -v error -y -ss $(( $2 + 0.5 )) -i "$1" -frames:v 1 -vf scale=1600:-2 -q:v 3 $O/$4.jpg; }
loop "$R" 12 5 court
loop "$R" 126.5 4 swish
loop "$T" 214 6 press
loop "$T" 30 6 title
loop "$T" 366 9 outro
loop "$T" 318 7 classroom
loop "$R" 115 7 drive
ffmpeg -v error -y -ss 26.5 -i "$T" -frames:v 1 -vf scale=1920:-2 -q:v 3 $O/hero_reel.jpg
# full trailer w/ audio, 720p
ffmpeg -v error -y -i "$T" -vf scale=1280:-2 -c:v libx264 -preset slow -crf 28 -maxrate 1400k -bufsize 2800k -pix_fmt yuv420p -c:a aac -b:a 112k -movflags +faststart $O/trailer_720p.mp4
ffmpeg -v error -y -ss 33 -i "$T" -frames:v 1 -vf scale=1920:-2 -q:v 3 $O/trailer_720p.jpg
rm -rf $O/tmp
ls -la $O
