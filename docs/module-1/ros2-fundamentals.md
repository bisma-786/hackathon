---
sidebar_position: 3
---

# Chapter 1.2: ROS 2 Fundamentals

## Learning Objectives
After completing this chapter, you will be able to:
- Explain the architecture and core concepts of ROS 2
- Describe the different communication patterns in ROS 2 (topics, services, actions)
- Understand the middleware implementations used in ROS 2
- Implement basic ROS 2 nodes and communication patterns
- Recognize the advantages of ROS 2 over ROS 1

## Introduction to ROS 2

Robot Operating System 2 (ROS 2) is a flexible framework for writing robot software that addresses the limitations of the original ROS while maintaining its core philosophy of distributed computation and code reuse. Unlike its predecessor, ROS 2 is designed from the ground up to be suitable for production environments with improved real-time capabilities, security, and reliability.

### Why ROS 2?

ROS 2 was developed to address several key limitations of ROS 1:

- **Real-time Support**: Better support for real-time systems required in production robotics
- **Security**: Built-in security features for safe deployment in industrial environments
- **Quality of Service (QoS)**: Configurable communication policies for different application needs
- **Multi-platform Support**: Native support for Windows, macOS, and Linux
- **Standard Compliance**: Adherence to DDS (Data Distribution Service) standards
- **Lifecycle Management**: Improved node lifecycle and system management

## Architecture Overview

ROS 2 follows a distributed computing architecture where multiple processes (nodes) communicate over a network. The key architectural components include:

### Nodes
Nodes are the fundamental units of computation in ROS 2. Each node is responsible for a specific task and communicates with other nodes through topics, services, or actions. Nodes are implemented as processes that can run on the same machine or distributed across multiple machines.

### Communication Primitives

#### Topics (Publish/Subscribe)
Topics implement a publish/subscribe communication pattern where publishers send messages to a topic and subscribers receive messages from the same topic. This is an asynchronous, decoupled communication method ideal for streaming data like sensor readings.

#### Services (Request/Reply)
Services implement a synchronous request/reply communication pattern where a client sends a request and waits for a response from a server. This is suitable for operations that have a clear input/output relationship.

#### Actions (Goal/Feedback/Result)
Actions implement a goal-oriented communication pattern with continuous feedback during execution. This is ideal for long-running tasks where clients need to monitor progress, cancel operations, or receive intermediate results.

### Middleware Layer

ROS 2 uses DDS (Data Distribution Service) as its underlying communication middleware. DDS provides:

- **Discovery**: Automatic discovery of nodes and their interfaces
- **Transport**: Reliable message delivery across networks
- **Quality of Service**: Configurable policies for reliability, durability, and liveliness
- **Security**: Authentication, encryption, and access control

Popular DDS implementations in ROS 2 include:
- **Fast DDS**: Developed by eProsima, widely used and well-supported
- **Cyclone DDS**: Developed by ADLINK, known for high performance
- **RTI Connext DDS**: Commercial solution with enterprise features

## Setting Up ROS 2

### Installation
ROS 2 supports multiple distributions, with the latest being Rolling Ridley. Popular stable distributions include Humble Hawksbill (Ubuntu 22.04 LTS) and Iron Irwini (Ubuntu 22.04 LTS).

```bash
# Install ROS 2 using the official installation guide
# For Ubuntu:
sudo apt update
sudo apt install ros-humble-desktop
```

### Environment Setup
ROS 2 requires sourcing the setup script to configure the environment:

```bash
source /opt/ros/humble/setup.bash
```

For persistent setup, add this line to your `~/.bashrc` file.

## Creating a ROS 2 Package

ROS 2 packages are the basic building blocks of ROS 2 applications:

```bash
# Create a new package
ros2 pkg create --build-type ament_cmake my_robot_package
```

A typical package structure includes:
- `CMakeLists.txt`: Build configuration for C++
- `package.xml`: Package metadata
- `src/`: Source code
- `include/`: Header files
- `launch/`: Launch files for starting multiple nodes
- `config/`: Configuration files

## Basic ROS 2 Programming

### Creating a Publisher Node (Python)

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Creating a Subscriber Node (Python)

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Quality of Service (QoS) Profiles

QoS profiles allow customization of communication behavior to meet specific application requirements:

### Reliability Policy
- **Reliable**: All messages are guaranteed to be delivered
- **Best Effort**: Messages may be lost, but delivery is faster

### Durability Policy
- **Transient Local**: Late-joining subscribers receive the last published message
- **Volatile**: Only new messages are sent to subscribers

### History Policy
- **Keep Last**: Maintain a fixed number of samples
- **Keep All**: Store all samples (limited by resource availability)

### Example QoS Configuration

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

qos_profile = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE
)
```

## Launch Files

Launch files allow starting multiple nodes with a single command:

```xml
<!-- launch/my_launch_file.launch.py -->
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot_package',
            executable='publisher_node',
            name='publisher',
            parameters=[
                {'param1': 'value1'},
                {'param2': 42}
            ]
        ),
        Node(
            package='my_robot_package',
            executable='subscriber_node',
            name='subscriber'
        )
    ])
```

## Services in ROS 2

Services provide synchronous request/response communication:

### Service Definition (.srv file)

```srv
# AddTwoInts.srv
int64 a
int64 b
---
int64 sum
```

### Service Server

```python
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning: {response.sum}')
        return response

def main(args=None):
    rclpy.init(args=args)
    minimal_service = MinimalService()
    rclpy.spin(minimal_service)
    rclpy.shutdown()
```

### Service Client

```python
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MinimalClientAsync(Node):
    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    minimal_client = MinimalClientAsync()
    response = minimal_client.send_request(1, 2)
    minimal_client.get_logger().info(f'Result of add_two_ints: {response.sum}')
    rclpy.shutdown()
```

## Actions in ROS 2

Actions are used for long-running tasks with feedback:

### Action Definition (.action file)

```
# Fibonacci.action
int32 order
---
int32[] sequence
---
int32[] feedback
```

### Action Server

```python
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class MinimalActionServer(Node):
    def __init__(self):
        super().__init__('minimal_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()

            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1])

            goal_handle.publish_feedback(feedback_msg)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        return result
```

## Testing and Debugging

### Command Line Tools
- `ros2 node list`: List active nodes
- `ros2 topic list`: List active topics
- `ros2 service list`: List available services
- `ros2 action list`: List active actions
- `ros2 topic echo <topic_name>`: Monitor topic messages
- `ros2 topic pub <topic_name> <msg_type> <values>`: Publish messages to a topic

### Visualization Tools
- **RViz2**: 3D visualization tool for robot data
- **rqt**: Graphical user interface for ROS
- **rosbag2**: Recording and playback of ROS data

## Best Practices

### Design Patterns
- **Modular Design**: Create focused nodes that perform specific functions
- **Interface Consistency**: Use standard message types when possible
- **Parameter Configuration**: Use parameters for configurable behavior
- **Logging**: Implement appropriate logging for debugging and monitoring

### Performance Considerations
- **Message Rate**: Balance update frequency with computational load
- **QoS Selection**: Choose appropriate QoS profiles for your application
- **Resource Management**: Monitor CPU, memory, and network usage
- **Threading**: Use appropriate threading models for concurrent operations

## Real-Time Considerations

ROS 2 supports real-time systems through:
- **Real-time capable DDS implementations**: Fast DDS RT
- **Linux PREEMPT_RT patches**: For deterministic scheduling
- **Isolated CPU cores**: Dedicated cores for time-critical tasks
- **Memory pre-allocation**: Avoid dynamic allocation during critical sections

## Security in ROS 2

Security features in ROS 2 include:
- **Authentication**: Verifying node identity
- **Encryption**: Protecting message content
- **Access Control**: Controlling node communication rights
- **Secure Discovery**: Preventing unauthorized node discovery

## Integration with Physical AI Systems

ROS 2 serves as the backbone for Physical AI systems by:
- Providing standardized interfaces between perception, cognition, and action components
- Enabling distributed computation across multiple hardware platforms
- Supporting real-time communication required for physical interaction
- Facilitating integration of third-party libraries and tools

## Key Takeaways

- ROS 2 is a distributed computing framework designed for production robotics
- It provides three communication patterns: topics, services, and actions
- QoS profiles allow customization of communication behavior
- ROS 2 addresses limitations of ROS 1 with real-time support and security
- Proper use of ROS 2 enables scalable and maintainable Physical AI systems

## Exercises

1. Create a ROS 2 package that implements a simple publisher-subscriber pair for exchanging sensor data (e.g., temperature readings).

2. Implement a service that performs a simple calculation (e.g., converting units) and test it with a client node.

3. Research and compare the different DDS implementations available for ROS 2. What are their strengths and weaknesses for different use cases?

4. Design a simple robot control system using ROS 2 nodes for sensor processing, decision making, and actuator control.

## Further Reading

- ROS 2 Documentation: https://docs.ros.org/en/humble/
- DDS Specification: https://www.omg.org/spec/DDS/
- "Programming Robots with ROS" by Morgan Quigley et al.
- "Effective Robotics Programming with ROS" by Anil Mahtani et al.