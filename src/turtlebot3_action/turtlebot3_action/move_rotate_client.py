import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from turtlebot3_interfaces.action import MoveAndRotate

class MoveNRotateClient(Node):
    def __init__(self):
        super().__init__('MoveAndRotateClient')
        self._client = ActionClient(self, MoveAndRotate, 'MoveAndRotate')

    def send_goal(self, distance, angle, timeout):
        self._client.wait_for_server()

        # Create goal message
        goal_msg = MoveAndRotate.Goal()
        goal_msg.distance = distance
        goal_msg.angle = angle
        goal_msg.timeout = timeout

        # Send goal asynchronously and register feedback + result callbacks
        self._send_goal_future = self._client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback):
        self.get_logger().info(f'Feedback: {feedback.feedback.current_state}, Progress: {feedback.feedback.progress:.2f}')

    def get_result_callback(self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info('Moving completed!')
        else:
            self.get_logger().info(f'Result: {result.message}')
            
def main():
    rclpy.init()
    client = MoveNRotateClient()
    client.send_goal(2.0, 90.0, 10.0)  # Send a goal with 2m distance, 90 degrees angle, and 10s timeout
    rclpy.spin(client)
    rclpy.shutdown()
