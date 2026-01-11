"""
NetBox RMS Mixins

提供可重用的模型 mixin
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utilities.choices import ChoiceSet


class ColorMixin:
    """
    为模型提供颜色获取功能的 Mixin
    
    用法：
        class MyModel(ColorMixin, NetBoxModel):
            status = models.CharField(choices=StatusChoices)
            
            def get_status_color(self):
                return self.get_color_for_field('status', StatusChoices)
    """
    
    def get_color_for_field(self, field_name: str, choice_class: 'ChoiceSet', default: str = 'secondary') -> str:
        """
        获取字段对应的颜色
        
        Args:
            field_name: 模型字段名
            choice_class: ChoiceSet 子类
            default: 默认颜色（当找不到匹配时）
            
        Returns:
            颜色类名（如 'blue', 'green', 'secondary'）
        """
        field_value = getattr(self, field_name, '')
        return choice_class.colors.get(field_value, default)
