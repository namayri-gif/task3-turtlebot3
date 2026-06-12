import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from turtlebot3_interfaces.action import MoveAndRotate

class MoveNRotateClient(Node):
    def __init__(self):
        super().__init__('square_action_client')
        self._client = ActionClient(self, DrawSquare, 'draw_square')

    def send_goal(self, side, reps):
        self._client.wait_for_server()

        # Create goal message
        goal_msg = DrawSquare.Goal()
        goal_msg.side_length = side
        goal_msg.repetitions = reps

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
        self.get_logger().info(f'Feedback: {feedback.feedback.status}')

    def get_result_callback(self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info('Square drawing completed!')
        else:
            self.get_logger().info('Failed to draw square.')

def main():
    rclpy.init()
    client = SquareClient()
    client.send_goal(2.0, 1)  # Send a goal with 2m side length and 1 repetition
    rclpy.spin(client)
    rclpy.shutdown()