# Face Tracking Cursor Monitor Switcher

---
 Forked from a cursor control eye tracking project, this program tracks which monitor you are looking at and flips the cursor between them accordingly.
## Progress (In partially descending order)
- [x] Basic version with MVP of proof of concept
- [ ] Monitor editor setup w/programmatic setup
  - [ ] Basic
  - [ ] Advanced
- [ ] Increased support to >2 monitors (programmatically)
- [ ] Better detection methods + w/ switching
- [ ] Use eye tracking instead of facial rotation to trigger monitor swap
- [ ] Automatic monitor count + general location detection
- [ ] Vertical separation monitor support
- [ ] Persistent settings storage 
- [ ] Efficiency overhaul (reoccurring as needed)
- [ ] Port and full shift to c++
- [ ] Cross-platform support/versions
- [ ] Test cases setup

## Default Runtime Controls
| Option               | Default Key/Location | Default Value | Description                                                                                                       |
|----------------------|:--------------------:|:-------------:|-------------------------------------------------------------------------------------------------------------------|
| Exit                 |      'esc', 'q'      |      n/a      | Exits the program completely as is (planned to also save options).                                                |
| Pause                |       spacebar       |     false     | Pauses the program, including relinquishing control of the camera.                                                |
| Auto Monitor #2      |         '2'          |      269      | Automatically sets second monitor trigger threshold between current facial position & 50% from straight on.       |
| Manual Monitor #2    |     Trackbar #1      |      45%      | Manually lets you configure through a scrollbar the left percentage for the cutoff point to switch to monitor #2. |
| Blank Background     |         's'          |     true      | Displays black background without camera feed for efficiency by only showing overlays and UI.                     |
| Allow Switch on Drag |         'd'          |     true      | Allows the monitor to switch when any mouse key is being pressed (any right now is the main 3).                   |
| Manual Blink         |         'b'          |     false     | Manually triggers detected blink. Blink used to switch between detection overlays.                                |
