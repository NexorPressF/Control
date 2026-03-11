#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        
        # Текущий статус робота
        self.current_status = ""
        self.previous_status = ""
        
        # Подписка на /robot_status
        self.status_sub = self.create_subscription(
            String,
            '/robot_status',
            self.status_callback,
            10
        )
        
        # Publisher для /cmd_vel
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Таймер для публикации команд с частотой 10 Hz
        self.timer = self.create_timer(0.1, self.timer_callback)  # 0.1 сек = 10 Hz
        
        self.get_logger().info("🤖 Robot Controller node started")
        self.get_logger().info("⏱️ Publishing commands at 10 Hz")
        self.get_logger().info("📡 Waiting for status messages...")
    
    def status_callback(self, msg):
        """Обновление статуса робота"""
        self.current_status = msg.data
        
        # Логируем изменение статуса
        if self.current_status != self.previous_status:
            self.get_logger().info(f"📨 Status received: '{self.current_status}'")
            self.previous_status = self.current_status
    
    def get_command_from_status(self):
        """Определение команды движения по статусу"""
        cmd = Twist()  # по умолчанию все поля = 0.0
        
        if self.current_status == "ALL OK":
            cmd.linear.x = 0.3
            cmd.angular.z = 0.0
            self.get_logger().debug("Command: Moving forward (0.3 m/s)", throttle_duration_sec=1.0)
            
        elif self.current_status == "WARNING: Low battery":
            cmd.linear.x = 0.1
            cmd.angular.z = 0.0
            self.get_logger().debug("Command: Moving slow (0.1 m/s)", throttle_duration_sec=1.0)
            
        elif self.current_status == "WARNING: Obstacle close":
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5  # поворот на месте
            self.get_logger().debug("Command: Rotating (0.5 rad/s)", throttle_duration_sec=1.0)
            
        elif self.current_status == "CRITICAL":
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0  # полная остановка
            self.get_logger().debug("Command: EMERGENCY STOP", throttle_duration_sec=1.0)
        
        return cmd
    
    def timer_callback(self):
        """Публикация команды каждые 0.1 секунды"""
        
        # Получаем команду для текущего статуса
        cmd = self.get_command_from_status()
        
        # Публикуем команду
        self.cmd_pub.publish(cmd)
        
        # Логируем первое движение или изменение статуса
        if not hasattr(self, 'last_logged_status') or self.last_logged_status != self.current_status:
            if self.current_status:
                action = self._get_action_description(cmd)
                self.get_logger().info(f"🚦 Mode changed: {self.current_status} → {action}")
                self.last_logged_status = self.current_status
    
    def _get_action_description(self, cmd):
        """Получение описания действия для логирования"""
        if abs(cmd.linear.x) > 0 and abs(cmd.angular.z) == 0:
            return f"Moving forward at {cmd.linear.x} m/s"
        elif abs(cmd.angular.z) > 0 and abs(cmd.linear.x) == 0:
            return f"Rotating at {cmd.angular.z} rad/s"
        elif cmd.linear.x == 0 and cmd.angular.z == 0:
            return "Stopped"
        else:
            return f"Moving: linear={cmd.linear.x}, angular={cmd.angular.z}"

def main(args=None):
    rclpy.init(args=args)
    node = RobotController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("👋 Robot Controller stopped by user")
        # При остановке отправляем команду STOP
        stop_cmd = Twist()
        node.cmd_pub.publish(stop_cmd)
        node.get_logger().info("🛑 Emergency stop command sent")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()