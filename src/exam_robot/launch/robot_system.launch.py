from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    # Путь к URDF файлу
    urdf_file = os.path.join(
        get_package_share_directory('exam_robot'),
        'urdf',
        'exam_robot.urdf'
    )
    
    # Чтение URDF файла для robot_description
    with open(urdf_file, 'r') as infp:
        robot_description_content = infp.read()
    
    # Параметр robot_description
    robot_description = {'robot_description': robot_description_content}
    
    return LaunchDescription([
        # ============ УЗЛЫ EXAM_ROBOT ============
        
        # Battery Node
        Node(
            package='exam_robot',
            executable='battery_node',
            name='battery_node',
            output='screen',
            parameters=[],
            arguments=[]
        ),
        
        # Distance Sensor
        Node(
            package='exam_robot',
            executable='distance_sensor',
            name='distance_sensor',
            output='screen',
            parameters=[],
            arguments=[]
        ),
        
        # Status Display
        Node(
            package='exam_robot',
            executable='status_display',
            name='status_display',
            output='screen',
            parameters=[],
            arguments=[]
        ),
        
        # Robot Controller
        Node(
            package='exam_robot',
            executable='robot_controller',
            name='robot_controller',
            output='screen',
            parameters=[],
            arguments=[]
        ),
        
        # ============ СТАНДАРТНЫЕ УЗЛЫ ROS2 ============
        
        # Robot State Publisher - публикует состояние робота из URDF
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description],
            arguments=[]
        ),
        
        # Joint State Publisher (опционально, для тестирования)
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[],
            arguments=[]
        ),
    ])
