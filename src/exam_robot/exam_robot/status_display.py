#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

class StatusDisplay(Node):
    def __init__(self):
        super().__init__('status_display')
        
        # Параметры
        self.battery_level = 100.0
        self.distance = 3.0
        self.current_status = ""
        self.previous_status = ""
        
        # Подписки
        self.battery_sub = self.create_subscription(
            Float32,
            '/battery_level',
            self.battery_callback,
            10
        )
        
        self.distance_sub = self.create_subscription(
            Float32,
            '/distance',
            self.distance_callback,
            10
        )
        
        # Publisher для /robot_status
        self.status_pub = self.create_publisher(String, '/robot_status', 10)
        
        # Таймер для публикации с частотой 2 Hz
        self.timer = self.create_timer(0.5, self.timer_callback)
        
        self.get_logger().info("🚦 Status Display node started")
        self.get_logger().info(f"📊 Initial: Battery={self.battery_level}%, Distance={self.distance}m")
    
    def battery_callback(self, msg):
        """Обновление уровня батареи"""
        old_battery = self.battery_level
        self.battery_level = msg.data
        
        # Логируем значительные изменения
        if abs(old_battery - self.battery_level) > 5.0:  # изменение больше 5%
            self.get_logger().info(f"🔋 Battery updated: {self.battery_level:.1f}%")
    
    def distance_callback(self, msg):
        """Обновление расстояния до препятствия"""
        old_distance = self.distance
        self.distance = msg.data
        
        # Логируем значительные изменения
        if abs(old_distance - self.distance) > 0.3:  # изменение больше 0.3м
            self.get_logger().info(f"📏 Distance updated: {self.distance:.2f}m")
    
    def determine_status(self):
        """Определение статуса робота по заданной логике"""
        
        # Проверка критических условий (приоритет 1)
        if self.battery_level < 10.0 or self.distance < 0.7:
            return "CRITICAL"
        
        # Проверка предупреждений
        elif self.battery_level < 20.0:
            return "WARNING: Low battery"
        
        elif self.distance < 1.0:
            return "WARNING: Obstacle close"
        
        # Все хорошо
        else:
            return "ALL OK"
    
    def timer_callback(self):
        """Публикация статуса каждые 0.5 секунд"""
        
        # Определяем текущий статус
        self.current_status = self.determine_status()
        
        # Публикуем статус
        status_msg = String()
        status_msg.data = self.current_status
        self.status_pub.publish(status_msg)
        
        # Логируем только при изменении статуса
        if self.current_status != self.previous_status:
            # Разные иконки для разных статусов
            icon = "✅" if self.current_status == "ALL OK" else "⚠️" if "WARNING" in self.current_status else "🔴"
            self.get_logger().info(f"{icon} Status changed: '{self.previous_status}' -> '{self.current_status}'")
            self.get_logger().info(f"   📊 Battery: {self.battery_level:.1f}%, Distance: {self.distance:.2f}m")
            self.previous_status = self.current_status
        
        # Отладка (каждые 2 секунды)
        self.get_logger().debug(
            f"Published status: {self.current_status} (B:{self.battery_level:.1f}%, D:{self.distance:.2f}m)",
            throttle_duration_sec=2.0
        )

def main(args=None):
    rclpy.init(args=args)
    node = StatusDisplay()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("👋 Status Display stopped by user")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()