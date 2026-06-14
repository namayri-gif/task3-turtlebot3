import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from turtlebot3_interfaces.action import MoveAndRotate
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math, time

class MoveNRotate(Node):
    def __init__(self):
        super().__init__('move_and_rotate_server')
        
        self.cb_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self, MoveAndRotate, 'MoveAndRotate', self.execute_callback,
            callback_group=self.cb_group)

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription_ = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10,
            callback_group=self.cb_group)

        self.x = 0.0
        self.y = 0.0

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    def execute_callback(self, goal_handle):
        self.get_logger().info('Goal received, executing...')

        feedback_msg = MoveAndRotate.Feedback()

        distance = goal_handle.request.distance
        angle    = goal_handle.request.angle
        timeout  = goal_handle.request.timeout

        start_time = time.time()

        # ── PHASE 1: MOVE FORWARD ────────────────────────────────────────────
        start_x = self.x
        start_y = self.y

        self.get_logger().info('Phase 1: Moving forward...')

        while True:
            time.sleep(0.1)  

            if time.time() - start_time > timeout:
                self.stop_robot()
                goal_handle.abort()
                result = MoveAndRotate.Result()
                result.success = False
                result.message = "Mission timeout"
                return result

            distance_traveled = math.sqrt(
                (self.x - start_x) ** 2 +
                (self.y - start_y) ** 2
            )

            if distance_traveled >= distance:
                break

            msg = Twist()
            msg.linear.x = 2.0
            self.publisher_.publish(msg)

            feedback_msg.current_state = "Moving"
            feedback_msg.progress = distance_traveled / distance
            goal_handle.publish_feedback(feedback_msg)

        self.stop_robot()
        self.get_logger().info('Phase 1 complete.')

        # ── PHASE 2: ROTATE ──────────────────────────────────────────────────
        angle_rad = math.radians(angle)
        angular_speed = 0.5
        rotate_duration = angle_rad / angular_speed

        self.get_logger().info('Phase 2: Rotating...')

        rotate_start = time.time()

        while True:
            time.sleep(0.1)

            if time.time() - start_time > timeout:
                self.stop_robot()
                goal_handle.abort()
                result = MoveAndRotate.Result()
                result.success = False
                result.message = "Mission timeout"
                return result

            elapsed_rotation = time.time() - rotate_start

            if elapsed_rotation >= rotate_duration:
                break

            msg = Twist()
            msg.angular.z = angular_speed
            self.publisher_.publish(msg)

            feedback_msg.current_state = "Rotating"
            feedback_msg.progress = elapsed_rotation / rotate_duration
            goal_handle.publish_feedback(feedback_msg)

        self.stop_robot()
        self.get_logger().info('Phase 2 complete.')

        # ── DONE ─────────────────────────────────────────────────────────────
        goal_handle.succeed()
        result = MoveAndRotate.Result()
        result.success = True
        result.message = "Mission completed successfully"
        return result

    def stop_robot(self):
        stop = Twist()
        stop.linear.x = 0.0
        stop.angular.z = 0.0
        self.publisher_.publish(stop)

def main():
    rclpy.init()
    node = MoveNRotate()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    main()
