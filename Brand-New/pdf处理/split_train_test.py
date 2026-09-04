import os
import pandas as pd

def split_train_test(df, train_size=5000, train_file='train.xlsx', test_file='test.xlsx'):
    # 打乱数据
    df_shuffled = df.sample(frac=1).reset_index(drop=True)
    
    # 分割数据
    train_df = df_shuffled.head(train_size)
    test_df = df_shuffled.tail(len(df_shuffled) - train_size)
    
    # 将训练集和测试集分别写入Excel文件
    train_df.to_excel(train_file, index=False)
    test_df.to_excel(test_file, index=False)

# 指定txt文件夹路径和输出Excel文件路径
merged_excel_file = r'D:\多模态\验证码\results.xlsx'  # 合并后的Excel文件路径
train_excel_file = r'D:\多模态\验证码\train.xlsx'  # 训练集Excel文件路径
test_excel_file = r'D:\多模态\验证码\test.xlsx'  # 测试集Excel文件路径

# 读取合并后的Excel文件
df = pd.read_excel(merged_excel_file)

# 分割为训练集和测试集
split_train_test(df, train_size=5000, train_file=train_excel_file, test_file=test_excel_file)



