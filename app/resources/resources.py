from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QByteArray, Qt, QRectF
from PySide6.QtSvg import QSvgRenderer


class IconEngine:
    # 核心图标库
    _ICONS = {
        "flashlight": '<path d="M13 10H20L11 23V14H4L13 1V10Z"/>',
        "circle": '<path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z"/>',
        "start": '<path d="M8 5v14l11-7z"/>',
        "stop": '<path d="M6 6h12v12H6z"/>',
        "link": '<path d="M10.59,13.41C11,13.8 11,14.44 10.59,14.83C10.2,15.22 9.56,15.22 9.17,14.83C7.22,12.88 7.22,9.71 9.17,7.76V7.76L12.71,4.22C14.66,2.27 17.83,2.27 19.78,4.22C21.73,6.17 21.73,9.34 19.78,11.29L18.29,12.78C18.3,11.96 18.17,11.14 17.89,10.36L18.36,9.88C19.54,8.71 19.54,6.81 18.36,5.64C17.19,4.46 15.29,4.46 14.12,5.64L10.59,9.17C9.41,10.34 9.41,12.24 10.59,13.41M13.41,9.17C13.8,8.78 14.44,8.78 14.83,9.17C16.78,11.12 16.78,14.29 14.83,16.24V16.24L11.29,19.78C9.34,21.73 6.17,21.73 4.22,19.78C2.27,17.83 2.27,14.66 4.22,12.71L5.71,11.22C5.7,12.04 5.83,12.86 6.11,13.65L5.64,14.12C4.46,15.29 4.46,17.19 5.64,18.36C6.81,19.54 8.71,19.54 9.88,18.36L13.41,14.83C14.59,13.66 14.59,11.76 13.41,10.59C13,10.2 13,9.56 13.41,9.17Z" />',
        "unlink": '<path d="M2,5.27L3.28,4L20,20.72L18.73,22L13.9,17.17L11.29,19.78C9.34,21.73 6.17,21.73 4.22,19.78C2.27,17.83 2.27,14.66 4.22,12.71L5.71,11.22C5.7,12.04 5.83,12.86 6.11,13.65L5.64,14.12C4.46,15.29 4.46,17.19 5.64,18.36C6.81,19.54 8.71,19.54 9.88,18.36L12.5,15.76L10.88,14.15C10.87,14.39 10.77,14.64 10.59,14.83C10.2,15.22 9.56,15.22 9.17,14.83C8.12,13.77 7.63,12.37 7.72,11L2,5.27M12.71,4.22C14.66,2.27 17.83,2.27 19.78,4.22C21.73,6.17 21.73,9.34 19.78,11.29L18.29,12.78C18.3,11.96 18.17,11.14 17.89,10.36L18.36,9.88C19.54,8.71 19.54,6.81 18.36,5.64C17.19,4.46 15.29,4.46 14.12,5.64L10.79,8.97L9.38,7.55L12.71,4.22M13.41,9.17C13.8,8.78 14.44,8.78 14.83,9.17C16.2,10.54 16.61,12.5 16.06,14.23L14.28,12.46C14.23,11.78 13.94,11.11 13.41,10.59C13,10.2 13,9.56 13.41,9.17Z" />',
        "trash": '<path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>',
        "save": '<path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/>',
        "file": '<path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>',
        "folder": '<path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>',
        "wait": '<path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>',
        "loop": '<path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>',
        "check": '<path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>',
        "send": '<path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>',
        "log": '<path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>',
        "config": '<path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L3.16 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.04.64.09.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>',
        "script": '<path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/>',
        "flash": '<path d="M7 2v11h3v9l7-12h-4l4-8z"/>',
        "add": '<path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z" />',
        "circles_add": '<path d="M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M13,7H11V11H7V13H11V17H13V13H17V11H13V7Z" />',
        "pencil": '<path d="M14.06,9L15,9.94L5.92,19H5V18.08L14.06,9M17.66,3C17.41,3 17.15,3.1 16.96,3.29L15.13,5.12L18.88,8.87L20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18.17,3.09 17.92,3 17.66,3M14.06,6.19L3,17.25V21H6.75L17.81,9.94L14.06,6.19Z" />',
        "refresh": '<path d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z" />',
        "auto_start": '<path d="M12.68 6H11.32L7 16H9L9.73 14H14.27L15 16H17L12.68 6M10.3 12.5L12 8L13.7 12.5H10.3M17.4 20.4L19 22H14V17L16 19C18.39 17.61 20 14.95 20 12C20 7.59 16.41 4 12 4S4 7.59 4 12C4 14.95 5.61 17.53 8 18.92V21.16C4.47 19.61 2 16.1 2 12C2 6.5 6.5 2 12 2S22 6.5 22 12C22 15.53 20.17 18.62 17.4 20.4Z" />',
        "tools": '<path d="M21.71 20.29L20.29 21.71A1 1 0 0 1 18.88 21.71L7 9.85A3.81 3.81 0 0 1 6 10A4 4 0 0 1 2.22 4.7L4.76 7.24L5.29 6.71L6.71 5.29L7.24 4.76L4.7 2.22A4 4 0 0 1 10 6A3.81 3.81 0 0 1 9.85 7L21.71 18.88A1 1 0 0 1 21.71 20.29M2.29 18.88A1 1 0 0 0 2.29 20.29L3.71 21.71A1 1 0 0 0 5.12 21.71L10.59 16.25L7.76 13.42M20 2L16 4V6L13.83 8.17L15.83 10.17L18 8H20L22 4Z" />',
        "car_connected": '<path d="M5,14H19L17.5,9.5H6.5L5,14M17.5,19A1.5,1.5 0 0,0 19,17.5A1.5,1.5 0 0,0 17.5,16A1.5,1.5 0 0,0 16,17.5A1.5,1.5 0 0,0 17.5,19M6.5,19A1.5,1.5 0 0,0 8,17.5A1.5,1.5 0 0,0 6.5,16A1.5,1.5 0 0,0 5,17.5A1.5,1.5 0 0,0 6.5,19M18.92,9L21,15V23A1,1 0 0,1 20,24H19A1,1 0 0,1 18,23V22H6V23A1,1 0 0,1 5,24H4A1,1 0 0,1 3,23V15L5.08,9C5.28,8.42 5.85,8 6.5,8H17.5C18.15,8 18.72,8.42 18.92,9M12,0C14.12,0 16.15,0.86 17.65,2.35L16.23,3.77C15.11,2.65 13.58,2 12,2C10.42,2 8.89,2.65 7.77,3.77L6.36,2.35C7.85,0.86 9.88,0 12,0M12,4C13.06,4 14.07,4.44 14.82,5.18L13.4,6.6C13.03,6.23 12.53,6 12,6C11.5,6 10.97,6.23 10.6,6.6L9.18,5.18C9.93,4.44 10.94,4 12,4Z" />',
        "format_list_group": '<path d="M5 5V19H7V21H3V3H7V5H5M20 7H7V9H20V7M20 11H7V13H20V11M20 15H7V17H20V15Z" />',

        # CANoe Style Tree Indicators (Box with + / -)
        # 注意：这里使用 stroke 绘制线条，fill=none
        "tree_plus": '<g stroke="currentColor" stroke-width="1.5" fill="none"><rect x="3" y="3" width="18" height="18"/><path d="M12 7v10M7 12h10"/></g>',
        "tree_minus": '<g stroke="currentColor" stroke-width="1.5" fill="none"><rect x="3" y="3" width="18" height="18"/><path d="M7 12h10"/></g>'
    }

    @staticmethod
    def get_icon(name: str, color: str = "#000000") -> QIcon:
        """
        生成指定颜色的 QIcon
        """
        path = IconEngine._ICONS.get(name, IconEngine._ICONS["file"])
        # 处理 currentColor 占位符 (用于 stroke)
        path = path.replace("currentColor", color)

        # 处理无 fill/stroke 的简单路径 (默认为 fill)
        if "fill=" not in path and "stroke=" not in path:
            content = f'<g fill="{color}">{path}</g>'
        else:
            content = path

        svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">{content}</svg>'

        renderer = QSvgRenderer(QByteArray(svg_content.encode('utf-8')))
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        # 强制渲染到 32x32 区域
        renderer.render(painter, QRectF(0, 0, 32, 32))
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def get_pixmap(name: str, color: str = "#000000", size: int = 24) -> QPixmap:
        """直接获取 Pixmap (用于 Label, ProxyStyle 等)"""
        return IconEngine.get_icon(name, color).pixmap(size, size)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout,
                                   QLabel, QScrollArea, QFrame)
    from PySide6.QtCore import Qt

    # 1. 初始化应用
    app = QApplication(sys.argv)

    # 2. 创建主窗口和滚动区域 (防止图标太多显示不全)
    main_window = QWidget()
    main_window.setWindowTitle("IconEngine 图标库预览")
    main_window.resize(600, 500)

    # 主布局
    main_layout = QVBoxLayout(main_window)

    # 滚动区设置
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    content_widget = QWidget()
    grid = QGridLayout(content_widget)  # 使用网格布局

    # 3. 遍历 IconEngine 中的所有图标并展示
    row, col = 0, 0
    MAX_COLS = 4  # 每行显示 4 个图标

    for name in IconEngine._ICONS.keys():
        # --- 创建一个小卡片容器 ---
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("QFrame { background-color: #f0f0f0; border-radius: 8px; }")
        card_layout = QVBoxLayout(card)

        # --- 设定颜色逻辑 (模拟不同状态) ---
        if name == "link":
            color = "#2ECC71"  # 绿色
        elif name == "unlink":
            color = "#E74C3C"  # 红色
        elif "tree" in name:
            color = "#555555"  # 深灰
        else:
            color = "#3498DB"  # 蓝色 (默认)

        # --- 获取图标 (调用您的 IconEngine) ---
        # 这里使用 48x48 的大图标方便查看
        pixmap = IconEngine.get_pixmap(name, color, size=48)

        # --- 显示图标 ---
        lbl_icon = QLabel()
        lbl_icon.setPixmap(pixmap)
        lbl_icon.setAlignment(Qt.AlignCenter)

        # --- 显示名字 ---
        lbl_text = QLabel(name)
        lbl_text.setAlignment(Qt.AlignCenter)
        lbl_text.setStyleSheet("color: #333; font-weight: bold;")

        # --- 添加到卡片 ---
        card_layout.addWidget(lbl_icon)
        card_layout.addWidget(lbl_text)

        # --- 添加到网格 ---
        grid.addWidget(card, row, col)

        # --- 网格换行逻辑 ---
        col += 1
        if col >= MAX_COLS:
            col = 0
            row += 1

    # 4. 组装并显示
    scroll.setWidget(content_widget)
    main_layout.addWidget(scroll)

    main_window.show()
    sys.exit(app.exec())