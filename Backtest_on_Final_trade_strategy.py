#!/usr/bin/env python
# coding: utf-8

# In[1]:


import lightgbm as lgb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
# Mount Google Drive if not already mounted
#from google.colab import drive


# Load the trained model
model = lgb.Booster(model_file='final_lgbm_model_original2.txt')


# Load the latest stock data
#data = pd.read_csv('/content/drive/MyDrive/backtest_data.csv（副本）')
data = pd.read_csv('backtest_data.csv（副本）')
data = pd.DataFrame(data,columns=["tradingDate","windCode","return"])
#print(data.loc[data['windCode'] == '600346.XSHG', 'return'].values)


# In[2]:


#Convert tradingDate and windCode of 2 datasets to same format 
import datetime
data2 = pd.read_csv('hs300_merged_market_data.csv')
dates = data2['tradingDate'].copy() # 创建数据副本

for i in range(len(dates)):
    date_str = dates[i]
    date_obj = pd.to_datetime(date_str, format='%Y/%m/%d')
    formatted_date_str = date_obj.strftime('%Y-%m-%d').replace('-', '-').replace('/', '-')
    formatted_date_str = '-'.join([d.zfill(2) for d in formatted_date_str.split('-')])
    dates[i] = formatted_date_str # 重新赋值到原始数据中

data2['tradingDate']=dates
data2['windCode'] = data2['windCode'].apply(lambda x: x.split('.')[1] + '.XSHE' if x.startswith('sz.') else x.split('.')[1] + '.XSHG')
print(data2)
#Use one example to validate code
print(data2.loc[data2['windCode'] == '600346.XSHG', 'close'].values)


# In[3]:


#Merge the close volumn with backtest_dataset
# 读取某些列，生成新的DataFrame
df2_data = pd.DataFrame(data2,columns=["tradingDate","windCode","close"])
print(data)
print(df2_data)
data=pd.merge(data,df2_data,how="inner",on=["tradingDate","windCode"])
print(data)


# In[4]:


selected_codes = data[data['tradingDate'] == '2021-11-01']['windCode'][data['return'].notnull()].unique()
print(selected_codes)

X_column_original=['alpha047', 'alpha076', 'alpha063', 'alpha115', 'alpha005', 'alpha057',
       'alpha139', 'alpha016', 'alpha145', 'alpha064', 'alpha008', 'alpha028',
       'alpha014', 'alpha121', 'alpha010', 'alpha127', 'alpha146', 'alpha066',
       'alpha108', 'alpha157', 'alpha078', 'alpha073', 'alpha041', 'alpha029',
       'alpha179', 'alpha170', 'alpha065', 'alpha062', 'alpha048', 'alpha159',
       'alpha070', 'alpha015', 'alpha022', 'alpha033', 'alpha168', 'alpha113',
       'alpha102', 'alpha074', 'alpha090', 'alpha025', 'alpha083', 'alpha104',
       'alpha006', 'alpha176', 'alpha019', 'alpha099', 'alpha018', 'alpha020',
       'alpha080', 'alpha001'] 
    
def X_input_original(filepath,date,code):
  data1=pd.read_csv(filepath)
  input=data1[(data1['tradingDate'] == date) & (data1['windCode'] == code)][X_column_original]
  return input

# Load input data for 2021-11-01
X_original = X_input_original('backtest_data.csv（副本）', '2021-11-01', selected_codes[0])

# Define the buy and sell thresholds
buy_threshold = 0.3
sell_threshold = -0.1


# In[5]:



# Calculate the predicted returns for all stocks in the backtest data for the target date
returns_backtest=[]
returns = []
for code in selected_codes:
  X = X_input_original('backtest_data.csv（副本）', '2021-11-01', code)
  predicted_return = model.predict(X)[0]
  returns.append((code, predicted_return))
  returns_backtest.append(predicted_return)


# Sort the returns in descending order
sorted_returns = sorted(returns, key=lambda x: x[1], reverse=True)

# Get the history closeprice for backtest
price = data[data['windCode'] == code]['close'].values[0]
ratio=[0.3,0.5]
portfolio_value_predict=[]
portfolio_value_reality=[]

for r in ratio:
    # Allocate the cash based on the predicted returns
    cash_remaining = 100000
    cash_remaining1 = 100000
    allocations = {}
    allocations1 = {}
    for i, (code, predicted_return) in enumerate(sorted_returns):
      if predicted_return >= buy_threshold:
        # Buy the stock
        allocation = cash_remaining * r#Iterate stock trading scenarios using different allocation ratios
        cash_remaining -= allocation#Ideal remaining cash equal to primary cash minus the allocation for buying stock
        allocations[code] = allocation#Allocate specific allocation to the corresponding stocks, storing them by code in allocations[]

        shares1 = allocation // price#According to real price,calculate the real shares number of stock buying
        #allocations1[code] = shares1
        cash_remaining1 -= shares1 * price#Update cash remaining after buying at real price


      elif predicted_return <= sell_threshold:
        # Sell the stock
        allocation = -allocations.get(code, 0)#Returns the current allocation for the given stock code or 0 if the code is not found in the dictionary
        cash_remaining += allocation#Ideal remaining cash equal to primary cash plus the allocation for buying stock
        allocations[code] = 0#Set the allocation of sold stock to zero
        
        cash_remaining1 += allocation * data[data['windCode'] == code]['close'].values[0]#Update cash remaining after selling at real price

    portfolio_value_reality.append(cash_remaining1)#Store the cash remaining in list to caculate
print(portfolio_value_reality)
    
# Plot the allocations
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(allocations.keys(), allocations.values())
ax.set_xlabel('Stock Code')
ax.set_ylabel('Allocation')
ax.set_title('Stock Allocations Based on Predicted Returns')
plt.show()

for code, allocation in sorted(allocations.items(), key=lambda x: x[1], reverse=True):
    print(f"{code}: {allocation}")
    


# We can utilize the trained lgbm model to forecast the next day's return value. As a result, in this trading technique, we initially chose a trading date of 2011.11.01 at random and screened out stocks with an increase rate on this date based on backtest data. Then we set a buy threshold of 0.3, a sell threshold of -0.1, and let's pretend we now have $100,000 cash. We then use a for loop to compute the anticipated returns for all the selected stocks in the backtest data for the target date and append the returns to a list. The output is the expected return on these stocks in 2021.11.02. Next,  we allocates the cash based on the predicted returns using another for loop. If the predicted return is greater than or  equal to the buy threshold,  it buys the stock by allocating 50% of the cash to these stock on a step-by-step basis.If the predicted return is less than or equal  to the sell threshold, it sells the stock by freeing up the allocation to that stock. Finally,  we plot the stock allocations using a bar plot with the stock codes on the x-axis and the allocations on the y-axis. The  plot is titled "Stock Allocations Based on Predicted Returns". and we print out the stocks we decided to buy in proportion  to their allotments

# #对每只股票进行不同持仓参数分配allocation，计算回测
# 
#     
#  Sell stocks
# for code in sell_stocks:
#     shares1 = int(allocations1.get(code, 0))
#     cash_remaining1 += shares1 * data[data['windCode'] == code]['close'].values[0]
#     allocations1[code] = 0
#     
#  Buy stocks
# for code in buy_stocks:
#     price = data[data['windCode'] == code]['close'].values[0]
#     allocation1 = int(cash_remaining1 / len(buy_stocks))
#     
#     shares1 = allocation1 // price
#     allocations1[code] = shares1
#     cash_remaining1 -= shares1 * price

# In[6]:


# Calculate the final portfolio value in different ratio and compare
for i, value in enumerate(portfolio_value_reality):
    for code, shares in allocations.items():
        #Multiplying the number of shares by the current market price, and adds it to the current total value of the portfolio
        value += shares * data[data['windCode'] == code]['close'].values[0]# Calculate portfolio_value_reality
    print(f"buy_threshold,sell_threshold: {buy_threshold,sell_threshold},Ratio: {ratio[i]}, Final portfolio real value: {value}")


#  Calculate the final portfolio value
# portfolio_value1 = cash_remaining1
# for code, shares1 in allocations1.items():
#     portfolio_value1 += shares1 * data[data['windCode'] == code]['close'].values[0]
# print(f"Final portfolio value1: {portfolio_value1}")

# #简单方法计算总收益，但allocation不准确
# cash=0
# Loop through the selected codes
# for code in allocations.keys():
#     # Get the closing price for the stock
#     close_price = data[data['windCode'] == code]['close'].values[0]
#     
#     # Calculate the return for the stock
#     allocation = allocations[code]
#     shares = allocation / close_price
#     current_value = shares * close_price
#     total_return = (current_value - allocation) / allocation
#     
#     # Update the cash balance
#     cash += current_value
#     
# Calculate the final portfolio value
# portfolio_value = cash
#     
# print(portfolio_value)

#     # Determine which stocks to buy or sell
#     buy_stocks = []
#     sell_stocks = []
#     for code in data[data['tradingDate'] == date]['windCode']:
#         if code in allocations:
#             current_return = backtest_data[(backtest_data['tradingDate'] == date) & (backtest_data['windCode'] == code)]['return'].values[0]
#             if current_return <= sell_threshold:
#                 sell_stocks.append(code)
#         else:
#             predicted_return = model.predict(X_input_original('backtest_data.csv（副本）', date, code))[0]
#             if predicted_return >= buy_threshold:
#                 buy_stocks.append(code)
#     
#     # Sell stocks
#     for code in sell_stocks:
#         shares = allocations.pop(code)
#         cash += shares * backtest_data[(backtest_data['tradingDate'] == date) & (backtest_data['windCode'] == code)]['close'].values[0]
#     
#     # Buy stocks
#     for code in buy_stocks:
#         price = backtest_data[(backtest_data['tradingDate'] == date) & (backtest_data['windCode'] == code)]['close'].values[0]
#         allocation = cash / len(buy_stocks)
#         shares = allocation // price
#         holdings[code] = shares
#         cash -= shares * price

# In[12]:


# Calculate the standard deviation of predicted returns
std_dev = np.std(returns_backtest)

# Calculate the Sharpe ratio
sharpe_ratio = np.mean(returns_backtest) / std_dev

# Print the results
print(f'Standard deviation: {std_dev:.4f}')
print(f'Sharpe ratio: {sharpe_ratio:.4f}')


# In[10]:


# Calculate the maximum drawdown
cum_return = np.cumprod(1 + returns_backtest) - 1
max_drawdown = np.max(np.maximum.accumulate(cum_return) - cum_return)

# Print the results
print(f'Standard deviation: {std_dev:.4f}')
print(f'Sharpe ratio: {sharpe_ratio:.4f}')
print(f'Maximum drawdown: {max_drawdown:.4f}')


# In[ ]:




