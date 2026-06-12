import rclpy                          # ROS client library for Python
from rclpy.node import Node           # Base Node class
from rclpy.action import ActionServer # Import Action Server
from turtlebot3_interfaces.action import MoveAndRotate  # Custom Action
from geometry_msgs.msg import Twist   # For controlling turtle
import math, time                     # Needed for motion calculations and delays

class MoveNRotate(Node):
    def __init__(self):
        super().__init__('square_action_server')

        # Create action server named 'draw_square'
        self._action_server = ActionServer(
            self, DrawSquare, 'draw_square', self.execute_callback)

        # Publisher to control turtle velocity
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

    async def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        # Create feedback message object
        feedback_msg = DrawSquare.Feedback()

        side = goal_handle.request.side_length
        reps = goal_handle.request.repetitions

        for r in range(reps):
            for i in range(4):
                feedback_msg.status = f'Side {i+1} of square {r+1}'
                goal_handle.publish_feedback(feedback_msg)  # Send feedback

                move_cmd = Twist()
                move_cmd.linear.x = 2.0  # Move forward
                self.publisher_.publish(move_cmd)
                time.sleep(side / 2.0)   # Sleep proportional to side length

                self.publisher_.publish(Twist())  # Stop
                time.sleep(0.5)

                turn_cmd = Twist()
                turn_cmd.angular.z = math.pi / 2.0  # 90 degrees turn
                self.publisher_.publish(turn_cmd)
                time.sleep(1.0)

                self.publisher_.publish(Twist())  # Stop
                time.sleep(0.5)

        goal_handle.succeed()
        return DrawSquare.Result(success=True)

def main():
    rclpy.init()
    node = SquareActionServer()
    rclpy.spin(node)
    rclpy.shutdown()
