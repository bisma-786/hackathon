---
sidebar_position: 7
---

# Chapter 1.6: Module 1 Capstone Exercise - Building a Simple Physical AI System

## Learning Objectives
After completing this capstone exercise, you will be able to:
- Integrate the concepts learned in Module 1 to build a simple Physical AI system
- Apply ROS 2 principles to coordinate multiple components
- Implement sensor integration and actuator control in a unified system
- Demonstrate embodied intelligence principles in a practical application
- Evaluate the performance of a Physical AI system

## Overview

In this capstone exercise, you will design and implement a simple Physical AI system: a mobile robot that navigates to a target location while avoiding obstacles. This system will integrate all the concepts covered in Module 1:

- **Physical AI Fundamentals**: Understanding the integration of perception, cognition, and action
- **ROS 2 Architecture**: Using ROS 2 for system integration and communication
- **Sensor Integration**: Combining multiple sensors for environmental awareness
- **Actuator Control**: Implementing precise control for robot motion
- **Embodied Intelligence**: Demonstrating how the robot's physical form and environment interaction enable intelligent behavior

## System Requirements

### Functional Requirements
1. The robot must detect obstacles in its environment using sensors
2. The robot must navigate toward a specified target location
3. The robot must avoid obstacles while maintaining progress toward the target
4. The robot must operate safely without collisions
5. The robot must provide feedback on its current state and intentions

### Non-Functional Requirements
1. The system must operate in real-time (response time < 100ms)
2. The system must be robust to sensor noise and environmental variations
3. The system must be modular and extensible for future enhancements
4. The system must follow ROS 2 best practices for node design and communication

## System Architecture

The system will consist of several interconnected ROS 2 nodes:

```
[Sensor Node] → [Perception Node] → [Planning Node] → [Control Node] → [Robot Hardware]
     ↑              ↑                   ↑              ↑
     └── [Visualization Node] ←──────────┘              │
                                                        │
[Target Publisher] ←────────────────────────────────────┘
```

### Node Descriptions

#### Sensor Node
- **Purpose**: Interface with physical sensors (simulated in this exercise)
- **Publishes**: `sensor_msgs/LaserScan` for obstacle detection
- **Subscribes**: None
- **Configuration**: Simulated LiDAR with 360° field of view

#### Perception Node
- **Purpose**: Process sensor data to identify obstacles and free space
- **Publishes**: Processed obstacle information and environment map
- **Subscribes**: `sensor_msgs/LaserScan` from sensor node
- **Functionality**: Obstacle detection, environment mapping

#### Planning Node
- **Purpose**: Generate navigation plans based on target and environment
- **Publishes**: `geometry_msgs/Twist` commands for robot motion
- **Subscribes**: Processed sensor data, target location
- **Functionality**: Path planning, obstacle avoidance, goal seeking

#### Control Node
- **Purpose**: Execute motion commands on the robot
- **Publishes**: Commands to robot hardware interface
- **Subscribes**: `geometry_msgs/Twist` from planning node
- **Functionality**: Low-level motion control, safety monitoring

#### Visualization Node
- **Purpose**: Display system state for monitoring and debugging
- **Publishes**: Visualization messages for RViz2
- **Subscribes**: All relevant system messages
- **Functionality**: System state visualization

## Implementation Steps

### Step 1: Environment Setup

First, create the ROS 2 package for the capstone project:

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python physical_ai_capstone
cd physical_ai_capstone
```

Create the necessary directory structure:

```
physical_ai_capstone/
├── launch/
├── config/
├── scripts/
├── test/
├── setup.py
├── setup.cfg
└── package.xml
```

### Step 2: Sensor Node Implementation

Create the sensor node that simulates LiDAR data:

```python
# scripts/sensor_node.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Header
import math
import random

class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')
        self.publisher = self.create_publisher(LaserScan, 'scan', 10)

        # Timer for publishing sensor data
        self.timer = self.create_timer(0.1, self.publish_scan)

        # Simulated environment parameters
        self.angle_min = -math.pi
        self.angle_max = math.pi
        self.angle_increment = 0.0174  # ~1 degree
        self.scan_time = 0.1
        self.range_min = 0.1
        self.range_max = 10.0

    def publish_scan(self):
        msg = LaserScan()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser_frame'

        # Set scan parameters
        msg.angle_min = self.angle_min
        msg.angle_max = self.angle_max
        msg.angle_increment = self.angle_increment
        msg.time_increment = 0.0
        msg.scan_time = self.scan_time
        msg.range_min = self.range_min
        msg.range_max = self.range_max

        # Generate simulated scan data
        num_readings = int((self.angle_max - self.angle_min) / self.angle_increment)
        msg.ranges = []

        for i in range(num_readings):
            angle = self.angle_min + i * self.angle_increment

            # Simulate obstacles in the environment
            distance = self.range_max  # Default to max range

            # Add some simulated obstacles
            if 0.5 < abs(angle) < 0.7:  # Front-left obstacle
                distance = 2.0 + random.uniform(-0.1, 0.1)
            elif -0.7 < angle < -0.5:  # Front-right obstacle
                distance = 2.2 + random.uniform(-0.1, 0.1)
            elif abs(angle) < 0.1:  # Front obstacle
                distance = 3.0 + random.uniform(-0.2, 0.2)

            msg.ranges.append(min(distance, self.range_max))

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    sensor_node = SensorNode()
    rclpy.spin(sensor_node)
    sensor_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step 3: Perception Node Implementation

Create the perception node that processes sensor data:

```python
# scripts/perception_node.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray, Header
import numpy as np
from collections import deque

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')

        # Subscriptions
        self.scan_subscription = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10)

        # Publications
        self.obstacle_pub = self.create_publisher(
            Float32MultiArray, 'obstacles', 10)
        self.free_space_pub = self.create_publisher(
            Float32MultiArray, 'free_space', 10)

        # Parameters
        self.obstacle_threshold = 1.0  # meters
        self.safe_distance = 0.5       # meters

        # Data structures for processing
        self.scan_buffer = deque(maxlen=5)  # Average over 5 scans

    def scan_callback(self, msg):
        # Store scan for averaging
        self.scan_buffer.append(msg.ranges)

        # Average recent scans to reduce noise
        if len(self.scan_buffer) > 0:
            avg_ranges = np.mean(list(self.scan_buffer), axis=0)
        else:
            avg_ranges = np.array(msg.ranges)

        # Process scan data to identify obstacles and free space
        angle_increment = msg.angle_increment
        angle_min = msg.angle_min

        obstacles = []
        free_space = []

        for i, range_val in enumerate(avg_ranges):
            angle = angle_min + i * angle_increment

            if not np.isnan(range_val) and range_val < self.obstacle_threshold:
                # Obstacle detected
                obstacles.append([angle, range_val])
            elif range_val > self.obstacle_threshold * 2:
                # Free space detected
                free_space.append([angle, range_val])

        # Publish obstacle information
        if obstacles:
            obstacle_msg = Float32MultiArray()
            obstacle_msg.layout.data_offset = 0
            obstacle_data = []
            for obs in obstacles:
                obstacle_data.extend(obs)
            obstacle_msg.data = obstacle_data
            self.obstacle_pub.publish(obstacle_msg)

        # Publish free space information
        if free_space:
            free_space_msg = Float32MultiArray()
            free_space_msg.layout.data_offset = 0
            free_space_data = []
            for fs in free_space:
                free_space_data.extend(fs)
            free_space_msg.data = free_space_data
            self.free_space_pub.publish(free_space_msg)

def main(args=None):
    rclpy.init(args=args)
    perception_node = PerceptionNode()
    rclpy.spin(perception_node)
    perception_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step 4: Planning Node Implementation

Create the planning node that generates navigation commands:

```python
# scripts/planning_node.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import Float32MultiArray, Bool
import numpy as np
import math

class PlanningNode(Node):
    def __init__(self):
        super().__init__('planning_node')

        # Subscriptions
        self.scan_subscription = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10)
        self.obstacle_subscription = self.create_subscription(
            Float32MultiArray, 'obstacles', self.obstacle_callback, 10)

        # Publications
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.status_pub = self.create_publisher(Bool, 'navigation_active', 10)

        # Target parameters (fixed for this exercise)
        self.target_x = 5.0
        self.target_y = 0.0
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.target_threshold = 0.5  # meters to target

        # Control parameters
        self.linear_speed = 0.5
        self.angular_speed = 0.5
        self.obstacle_avoidance_distance = 1.0

        # State variables
        self.obstacles = []
        self.closest_obstacle = float('inf')

        # Timer for planning loop
        self.timer = self.create_timer(0.05, self.plan_and_control)

    def scan_callback(self, msg):
        # Process scan to find closest obstacle
        if msg.ranges:
            valid_ranges = [r for r in msg.ranges if not math.isnan(r) and r > 0]
            if valid_ranges:
                self.closest_obstacle = min(valid_ranges)

    def obstacle_callback(self, msg):
        # Store obstacle information
        if len(msg.data) >= 2:
            # Convert flat array back to [angle, distance] pairs
            self.obstacles = []
            for i in range(0, len(msg.data), 2):
                if i + 1 < len(msg.data):
                    self.obstacles.append([msg.data[i], msg.data[i + 1]])

    def plan_and_control(self):
        cmd_vel = Twist()

        # Check if we're close to target
        distance_to_target = math.sqrt(
            (self.target_x - self.robot_x)**2 + (self.target_y - self.robot_y)**2)

        if distance_to_target < self.target_threshold:
            # Reached target
            cmd_vel.linear = Vector3(x=0.0, y=0.0, z=0.0)
            cmd_vel.angular = Vector3(x=0.0, y=0.0, z=0.0)
            self.get_logger().info('Target reached!')
        else:
            # Need to navigate to target
            if self.closest_obstacle < self.obstacle_avoidance_distance:
                # Obstacle avoidance mode
                cmd_vel = self.avoid_obstacles()
            else:
                # Go-to-goal mode
                cmd_vel = self.go_to_goal()

        # Publish command
        self.cmd_vel_pub.publish(cmd_vel)

        # Publish navigation status
        status_msg = Bool()
        status_msg.data = distance_to_target > self.target_threshold
        self.status_pub.publish(status_msg)

    def go_to_goal(self):
        cmd_vel = Twist()

        # Simple proportional controller for going to goal
        # In a real implementation, this would use more sophisticated path planning
        cmd_vel.linear.x = min(self.linear_speed, 0.5)  # Move forward
        cmd_vel.angular.z = 0.0  # No rotation for now

        return cmd_vel

    def avoid_obstacles(self):
        cmd_vel = Twist()

        # Simple obstacle avoidance: turn away from closest obstacles
        if self.obstacles:
            # Find obstacles in front of robot
            front_obstacles = [obs for obs in self.obstacles if abs(obs[0]) < math.pi/3]

            if front_obstacles:
                # Average angle of front obstacles
                avg_angle = sum(obs[0] for obs in front_obstacles) / len(front_obstacles)

                # Turn away from obstacles
                if avg_angle > 0:
                    # Obstacles on the right, turn left
                    cmd_vel.angular.z = self.angular_speed
                    cmd_vel.linear.x = 0.0  # Stop moving forward
                else:
                    # Obstacles on the left, turn right
                    cmd_vel.angular.z = -self.angular_speed
                    cmd_vel.linear.x = 0.0  # Stop moving forward
            else:
                # No front obstacles, continue forward
                cmd_vel.linear.x = self.linear_speed
                cmd_vel.angular.z = 0.0
        else:
            # No obstacles detected, go forward
            cmd_vel.linear.x = self.linear_speed
            cmd_vel.angular.z = 0.0

        return cmd_vel

def main(args=None):
    rclpy.init(args=args)
    planning_node = PlanningNode()
    rclpy.spin(planning_node)
    planning_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step 5: Control Node Implementation

Create the control node that executes commands:

```python
# scripts/control_node.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
import time

class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        # Subscriptions
        self.cmd_vel_subscription = self.create_subscription(
            Twist, 'cmd_vel', self.cmd_vel_callback, 10)
        self.status_subscription = self.create_subscription(
            Bool, 'navigation_active', self.status_callback, 10)

        # Simulated robot state
        self.current_velocity = Twist()
        self.is_navigating = False
        self.safety_enabled = True

        # Safety parameters
        self.max_linear_speed = 1.0
        self.max_angular_speed = 1.0
        self.emergency_stop_distance = 0.3

        # Timer for safety checks
        self.safety_timer = self.create_timer(0.1, self.safety_check)

    def cmd_vel_callback(self, msg):
        # Apply safety limits to commands
        safe_msg = Twist()

        # Limit linear velocity
        safe_msg.linear.x = max(-self.max_linear_speed,
                               min(self.max_linear_speed, msg.linear.x))
        safe_msg.linear.y = max(-self.max_linear_speed,
                               min(self.max_linear_speed, msg.linear.y))
        safe_msg.linear.z = max(-self.max_linear_speed,
                               min(self.max_linear_speed, msg.linear.z))

        # Limit angular velocity
        safe_msg.angular.x = max(-self.max_angular_speed,
                                min(self.max_angular_speed, msg.angular.x))
        safe_msg.angular.y = max(-self.max_angular_speed,
                                min(self.max_angular_speed, msg.angular.y))
        safe_msg.angular.z = max(-self.max_angular_speed,
                                min(self.max_angular_speed, msg.angular.z))

        # Store current command
        self.current_velocity = safe_msg

        # Log the command (in a real system, this would control actual hardware)
        self.get_logger().debug(f'Command: linear={safe_msg.linear.x:.2f}, '
                               f'angular={safe_msg.angular.z:.2f}')

    def status_callback(self, msg):
        self.is_navigating = msg.data

    def safety_check(self):
        # Perform safety checks
        if self.safety_enabled and not self.is_navigating:
            # Navigation complete, stop robot
            stop_cmd = Twist()
            self.current_velocity = stop_cmd
            self.get_logger().info('Navigation complete - robot stopped')

def main(args=None):
    rclpy.init(args=args)
    control_node = ControlNode()
    rclpy.spin(control_node)
    control_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step 6: Visualization Node Implementation

Create the visualization node:

```python
# scripts/visualization_node.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray, Bool
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
import math

class VisualizationNode(Node):
    def __init__(self):
        super().__init__('visualization_node')

        # Subscriptions
        self.scan_subscription = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10)
        self.obstacle_subscription = self.create_subscription(
            Float32MultiArray, 'obstacles', self.obstacle_callback, 10)
        self.cmd_vel_subscription = self.create_subscription(
            Twist, 'cmd_vel', self.cmd_vel_callback, 10)
        self.status_subscription = self.create_subscription(
            Bool, 'navigation_active', self.status_callback, 10)

        # Publications
        self.marker_pub = self.create_publisher(MarkerArray, 'visualization_markers', 10)

        # Visualization data
        self.scan_ranges = []
        self.scan_angles = []
        self.obstacles = []
        self.cmd_vel = Twist()
        self.navigation_active = False

        # Timer for visualization updates
        self.timer = self.create_timer(0.1, self.publish_visualization)

    def scan_callback(self, msg):
        self.scan_ranges = msg.ranges
        self.scan_angles = [msg.angle_min + i * msg.angle_increment
                           for i in range(len(msg.ranges))]

    def obstacle_callback(self, msg):
        self.obstacles = []
        for i in range(0, len(msg.data), 2):
            if i + 1 < len(msg.data):
                self.obstacles.append([msg.data[i], msg.data[i + 1]])

    def cmd_vel_callback(self, msg):
        self.cmd_vel = msg

    def status_callback(self, msg):
        self.navigation_active = msg.data

    def publish_visualization(self):
        marker_array = MarkerArray()

        # Create obstacle markers
        obstacle_marker = Marker()
        obstacle_marker.header.frame_id = "laser_frame"
        obstacle_marker.header.stamp = self.get_clock().now().to_msg()
        obstacle_marker.ns = "obstacles"
        obstacle_marker.id = 0
        obstacle_marker.type = Marker.POINTS
        obstacle_marker.action = Marker.ADD

        # Set marker properties
        obstacle_marker.pose.orientation.w = 1.0
        obstacle_marker.scale.x = 0.1
        obstacle_marker.scale.y = 0.1
        obstacle_marker.color.r = 1.0
        obstacle_marker.color.a = 1.0

        # Add obstacle points
        for angle, distance in self.obstacles:
            point = Point()
            point.x = distance * math.cos(angle)
            point.y = distance * math.sin(angle)
            point.z = 0.0
            obstacle_marker.points.append(point)

        marker_array.markers.append(obstacle_marker)

        # Create robot status marker
        status_marker = Marker()
        status_marker.header.frame_id = "base_link"
        status_marker.header.stamp = self.get_clock().now().to_msg()
        status_marker.ns = "status"
        status_marker.id = 1
        status_marker.type = Marker.TEXT_VIEW_FACING
        status_marker.action = Marker.ADD

        status_marker.pose.position.z = 1.0
        status_marker.pose.orientation.w = 1.0
        status_marker.scale.z = 0.3
        status_marker.color.r = 1.0
        status_marker.color.g = 1.0
        status_marker.color.b = 1.0
        status_marker.color.a = 1.0
        status_marker.text = f"Nav: {'Active' if self.navigation_active else 'Complete'}\n" \
                            f"Lin: {self.cmd_vel.linear.x:.2f}, " \
                            f"Ang: {self.cmd_vel.angular.z:.2f}"

        marker_array.markers.append(status_marker)

        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    visualization_node = VisualizationNode()
    rclpy.spin(visualization_node)
    visualization_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Step 7: Launch File

Create a launch file to start all nodes:

```python
# launch/capstone_launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    return LaunchDescription([
        # Sensor node
        Node(
            package='physical_ai_capstone',
            executable='sensor_node',
            name='sensor_node',
            output='screen'
        ),

        # Perception node
        Node(
            package='physical_ai_capstone',
            executable='perception_node',
            name='perception_node',
            output='screen'
        ),

        # Planning node
        Node(
            package='physical_ai_capstone',
            executable='planning_node',
            name='planning_node',
            output='screen'
        ),

        # Control node
        Node(
            package='physical_ai_capstone',
            executable='control_node',
            name='control_node',
            output='screen'
        ),

        # Visualization node
        Node(
            package='physical_ai_capstone',
            executable='visualization_node',
            name='visualization_node',
            output='screen'
        )
    ])
```

### Step 8: Package Configuration

Update the setup.py file:

```python
# setup.py
from setuptools import setup
import os
from glob import glob

package_name = 'physical_ai_capstone'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Physical AI Capstone Exercise',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sensor_node = physical_ai_capstone.sensor_node:main',
            'perception_node = physical_ai_capstone.perception_node:main',
            'planning_node = physical_ai_capstone.planning_node:main',
            'control_node = physical_ai_capstone.control_node:main',
            'visualization_node = physical_ai_capstone.visualization_node:main',
        ],
    },
)
```

### Step 9: Package.xml

Update the package.xml file:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>physical_ai_capstone</name>
  <version>0.0.1</version>
  <description>Physical AI Capstone Exercise - Module 1</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>visualization_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

## Testing and Evaluation

### System Testing

1. **Build the package**:
```bash
cd ~/ros2_ws
colcon build --packages-select physical_ai_capstone
source install/setup.bash
```

2. **Launch the system**:
```bash
ros2 launch physical_ai_capstone capstone_launch.py
```

3. **Monitor the system**:
```bash
# Check active nodes
ros2 node list

# Monitor topics
ros2 topic echo /scan
ros2 topic echo /cmd_vel

# Visualize in RViz2 (if available)
rviz2
```

### Performance Evaluation

Evaluate the system based on:

1. **Navigation Success Rate**: Percentage of successful target acquisitions
2. **Obstacle Avoidance**: Ability to avoid collisions while navigating
3. **Efficiency**: Time and distance to reach target
4. **Robustness**: Performance under sensor noise and environmental variations
5. **Real-time Performance**: Meeting timing constraints

## Analysis Questions

After implementing and testing the system, consider these questions:

1. **Embodied Intelligence**: How does the physical form of the robot (sensors, actuators) influence its intelligent behavior? What aspects of intelligence emerge from the sensorimotor loop?

2. **System Integration**: How do the different components (sensing, perception, planning, control) work together to produce intelligent behavior? What happens when one component fails?

3. **Adaptability**: How would the system need to change to handle different environments or tasks? What aspects are general vs. task-specific?

4. **Scalability**: What challenges would arise if you tried to scale this system to more complex tasks or environments?

5. **Safety and Ethics**: What safety considerations are important for this type of system? How would you ensure safe operation around humans?

## Extensions and Improvements

Consider these potential improvements to the system:

1. **Advanced Path Planning**: Implement A* or Dijkstra's algorithm for more efficient navigation
2. **Dynamic Obstacles**: Handle moving obstacles in the environment
3. **Multi-Target Navigation**: Navigate to multiple targets in sequence
4. **Learning Capabilities**: Implement learning from experience to improve performance
5. **Human Interaction**: Add capabilities for human-robot interaction and collaboration

## Key Takeaways

This capstone exercise demonstrates several important principles of Physical AI:

- **Integration**: Physical AI systems require tight integration of sensing, cognition, and action
- **Embodiment**: The physical form and environmental interaction shape intelligent behavior
- **Real-time Operation**: Physical systems must operate in real-time with continuous sensorimotor loops
- **Robustness**: Systems must handle uncertainty, noise, and unexpected situations
- **Safety**: Safety considerations are paramount in physical systems

## Conclusion

The capstone exercise provides a practical demonstration of how the concepts from Module 1 come together in a real (simulated) system. By implementing each component and seeing how they interact, you gain insight into the challenges and opportunities of Physical AI development.

The system you've built serves as a foundation that can be extended with more sophisticated algorithms, additional sensors, and more complex behaviors. The modular architecture using ROS 2 provides a scalable approach for future development.

## Exercises for Further Learning

1. **Enhanced Perception**: Modify the perception node to implement more sophisticated obstacle detection algorithms.

2. **Alternative Planning**: Implement a different path planning algorithm (e.g., potential fields, RRT) and compare performance.

3. **Learning Component**: Add a learning mechanism that improves navigation performance over time.

4. **Multi-Robot System**: Extend the system to coordinate multiple robots working together.

5. **Real Hardware**: Adapt the system to run on actual robot hardware if available.

## Further Reading

- "Programming Robots with ROS" by Quigley et al.
- "Probabilistic Robotics" by Thrun, Burgard, and Fox
- "Introduction to Autonomous Robots" by Correll
- ROS 2 Navigation Stack Documentation
- "Robotics, Vision and Control" by Corke