# Task 3: TurtleBot3 ROS 2 Action Mission System

## Overview
This project implements a ROS 2 Action-based mission system for TurtleBot3 using Python.
The robot receives a goal containing a distance, angle, and timeout. It then executes the mission in two sequential phases:
Move Forward — using odometry to track real distance traveled
Rotate — using constant angular speed over a calculated duration
The project is divided into two ROS 2 packages:
`turtlebot3_interfaces` — Contains the custom action definition
`turtlebot3_action` — Contains the action server and client nodes

---
## Project Structure
```
task3-turtlebot3/
├── turtlebot3_interfaces/
│   ├── action/
│   │   └── MoveAndRotate.action
│   ├── CMakeLists.txt
│   └── package.xml
│
├── turtlebot3_action/
│   ├── turtlebot3_action/
│   │   ├── __init__.py
│   │   ├── move_rotate_server.py
│   │   └── move_rotate_client.py
│   ├── resource/
│   │   └── turtlebot3_action
│   ├── package.xml
│   ├── setup.cfg
│   └── setup.py
│
└── README.md
```
---
## Action Definition
File: `turtlebot3_interfaces/action/MoveAndRotate.action`
```
float32 distance
float32 angle
float32 timeout
---
bool success
string message
---
string current_state
float32 progress
```
## Field Meanings
Section	Field	Description
Goal	`distance`	Forward movement in meters
Goal	`angle`	Rotation in degrees
Goal	`timeout`	Maximum allowed execution time (seconds)
Result	`success`	Whether the mission completed
Result	`message`	Final status message
Feedback	`current_state`	Current phase: "Moving" or "Rotating"
Feedback	`progress`	Execution progress from 0.0 to 1.0

---
## System Behavior
Phase 1: Move Forward
Publishes velocity commands to `/cmd_vel`
Subscribes to `/odom` to track real distance traveled
Stops when `distance_traveled >= goal.distance`
Phase 2: Rotate
Uses constant angular speed (0.5 rad/s)
Calculates required duration from `angle / angular_speed`
Stops when elapsed rotation time is reached
Timeout Handling
A timer starts when the goal is accepted. If `elapsed_time > goal.timeout`:
Robot stops immediately
Action is aborted
Returns `success = false`, `message = "Mission timeout"`

---
## Topics Used
Topic	Type	Purpose
`/cmd_vel`	`geometry_msgs/msg/Twist`	Robot velocity commands
`/odom`	`nav_msgs/msg/Odometry`	Robot position tracking

---
## Requirements
ROS 2 Jazzy
TurtleBot3 packages
Gazebo Simulator
`geometry_msgs`
`nav_msgs`
`rclpy`

---
## Build
Clone the repository into your workspace and build both packages:
```bash

cd ros2_ws
colcon build
source install/setup.bash
```
---
### Launch
Step 1 — Start Gazebo simulation
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```
Step 2 — Run the Action Server
```bash
cd ros2_ws
source install/setup.bash
ros2 run turtlebot3_action move_rotate_server
```
Step 3 — Run the Action Client
```bash
cd ros2_ws
source install/setup.bash
ros2 run turtlebot3_action move_rotate_client
```
> Every new terminal needs `source install/setup.bash`
---
### Expected Output
Server terminal:
```
Goal received, executing...
Phase 1: Moving forward...
Phase 1 complete.
Phase 2: Rotating...
Phase 2 complete.
```
Client terminal:
```
State: Moving | Progress: 0.45
State: Moving | Progress: 0.87
State: Rotating | Progress: 0.30
State: Rotating | Progress: 0.95
Result: Mission completed successfully
```
---
## Verification
The system was tested using TurtleBot3 in Gazebo simulation. The following was verified:
Robot moves forward the specified distance using odometry feedback
Robot rotates the specified angle using time-based control
Continuous feedback is published throughout execution
Timeout correctly aborts the mission and stops the robot
Final result message is received by the client

---
### Server Terminal:
<img width="880" height="142" alt="Screenshot 2026-06-14 125527" src="https://github.com/user-attachments/assets/f69460ed-159a-456f-a047-6e21c0d04dd7" />

---
### Client Terminal: 
<img width="847" height="259" alt="Screenshot 2026-06-14 125514" src="https://github.com/user-attachments/assets/09def381-0915-4af3-9f79-d7f90d201c46" />


---
