import re

# 读取文件
with open(r'd:\Src\netbox-resourcemanagement\netbox_rms\models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 get_absolute_url 之后添加颜色方法  
insert_text = '''
    
    @property
    def get_task_type_color(self):
        """获取任务类型颜色"""
        return TaskTypeChoices.colors.get(self.task_type, 'secondary')
    
    @property
    def get_execution_status_color(self):
        """获取执行状态颜色"""
        return ExecutionStatusChoices.colors.get(self.execution_status, 'secondary')
    
    @property
    def get_execution_department_color(self):
        """获取执行部门颜色"""
        return ExecutionDepartmentChoices.colors.get(self.execution_department, 'secondary')
'''

# 找到TaskDetail的get_absolute_url位置
pos = content.find("# 执行任务详情模型")
url_end = content.find("def clean(self) -> None:", pos)

# 在clean方法之前插入
content = content[:url_end] + insert_text + '\n    ' + content[url_end:]

open(r'd:\Src\netbox-resourcemanagement\netbox_rms\models.py', 'w', encoding='utf-8').write(content)
print('✅ 已添加颜色方法到TaskDetail')
