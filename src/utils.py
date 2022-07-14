def prefilter_items(data, item_features, take_n_popular=5000):
    # Уберем самые популярные товары (их и так купят)
    # popularity = data.groupby('item_id')['user_id'].nunique().reset_index() / data['user_id'].nunique()
    # popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)
    
    user_count = data['user_id'].nunique()
    week_year_ago = data['week_no'].max() - 53

    popularity = data.groupby('item_id')['user_id'].nunique().reset_index() 
    popularity['user_id'] = popularity['user_id'] / user_count
    popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)
    top_popular = popularity[popularity['share_unique_users'] > 0.5].item_id.tolist()
    data = data[~data['item_id'].isin(top_popular)]
    
    # Уберем самые НЕ популярные товары (их и так НЕ купят)
    top_notpopular = popularity[popularity['share_unique_users'] < 0.01].item_id.tolist()
    data = data[~data['item_id'].isin(top_notpopular)]    
    
    # Уберем товары, которые не продавались за последние 12 месяцев
    # используем колонку week_no тут недели по возрастанию. 
    # По каждому товару берем максимальную неделю. Если она меньше data['week_no'].max() - 53 то не рассматриваем товар
    old_items = data.groupby('item_id')['week_no'].max().reset_index()
    old_items = old_items[old_items['week_no'] < week_year_ago].item_id.tolist()
    data = data[~data['item_id'].isin(old_items)]
    
    # Уберем не интересные для рекоммендаций категории (department)

    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб.
    # Уберем слишком дорогие товарыs
    data['item_price'] = 0
    data['item_price'] = data.apply(lambda x: x.sales_value if x.quantity == 0 else x.sales_value/x.quantity, axis=1)
    
    min_price = data.groupby('item_id')['item_price'].min().reset_index()
    max_price = data.groupby('item_id')['item_price'].max().reset_index()

    cheap_items = min_price[min_price['item_price'] < 1].item_id.tolist()
    expen_items = max_price[max_price['item_price'] > 300].item_id.tolist()

    data = data[~data['item_id'].isin(cheap_items)]
    data = data[~data['item_id'].isin(expen_items)]
  
    # и еще раз топ популярных из того что осталось
    sorted_popularity = popularity.sort_values(by='share_unique_users', ascending = False)
    top_popular = sorted_popularity.head(take_n_popular).item_id.tolist()    

    data = data[data['item_id'].isin(top_popular)]
    
    return data
    
    
def postfilter_items(user_id, recommednations):
    pass