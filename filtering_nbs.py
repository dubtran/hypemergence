'''
Here we go into the NBS json dump to retrieve the time series for various platforms, ie soundcloud, facebook
@param: d_arts: dictionary of values, media: which media we would like to filter out
@return : dictionary of the filtered data
'''
def filtering_data(d_arts, media): 
    art_sc = dict()
    for x in d_arts.keys():
        try:
            if media in d_arts[x].keys():
                 art_sc[x] = d_arts[x][media]
        except Exception, e:
            print e[0]
    return art_sc

'''
finding the log of plays and then their difference over days
@param: dict of artists and their timeseries
@return: dataframe of transformed data
''' 
def get_logmovement(artists):
    entire_difs = pd.DataFrame()

    for key, value in artists.iteritems():
        logged = pd.DataFrame(value)
        logged['plays'] = log(value['plays'])
        logged = logged.set_index('date')
        log_dif = logged.diff()
#         rr = log_dif.resample("W", how='mean')
#         _diff = move-rr
#         log_dif[key+'_reDif'] = _diff
        entire_difs = pd.concat([entire_difs,log_dif], axis = 1)
        entire_difs = entire_difs.rename(columns = {'plays': key})
    return entire_difs

'''
finding the log of the absolute value of the difference in plays per day 
@params: dict of artists and their timeseries
@return: dataframe of transformed values
'''
def get_absMovement(artists):
    entire_df = pd.DataFrame()
    for a, val in artists.iteritems():
        temp = pd.DataFrame(val)
        temp['plays'] = log(abs(temp['plays'].diff()))
        entire_df = pd.concat([entire_df, temp], axis = 1)
        entire_df = entire_df.rename(columns = {'plays': a})
    return entire_df

'''
helper method for creating dataframes
@params: metric: the type of metric from the social media platform, m_name: the name of the metric
@return: dataframe 
'''
def SC_df_helper(metric, m_name):
    
    play_df = pd.DataFrame.from_dict(metric)
    play_df.columns = ['date', m_name]
    play_df['date'] = pd.to_datetime(play_df['date'])
    play_df = play_df.sort('date').reset_index()
    play_df.pop('index')
    
    return play_df

'''
method creating the dataframes for plays/downloads/comments/fans/and combined
@params: dict of artists and their time series data
@return: dataframes
'''
def SCcreating_dfs(art_sc):
    dfs_plays = {}
    dfs_downloads = {}
    dfs_comments = {}
    dfs_fans = {}
    dfs_soundcloud = {}
    for x in art_sc.keys():

        if art_sc[x]['plays']:
            dfs_plays[ x.encode('ascii', errors = 'ignore').rstrip()] = SC_df_helper(art_sc[x]['plays'], 'plays') 

        if art_sc[x]['downloads']: 
            dfs_downloads[ x.encode('ascii', errors = 'ignore').rstrip()] = SC_df_helper(art_sc[x]['downloads'], 'downloads')

        if art_sc[x]['comments']:
            dfs_comments[x.encode('ascii', errors = 'ignore').rstrip()] = SC_df_helper(art_sc[x]['comments'], 'comments')

        if art_sc[x]['fans']:
            dfs_fans[x.encode('ascii', errors = 'ignore').rstrip()] = SC_df_helper(art_sc[x]['fans'], 'fans')

        full_df = pd.concat([play_df, download_df, comment_df, fan_df], axis = 1)
        dfs_soundcloud[x.encode('ascii', errors = 'ignore')] = full_df
    return dfs_plays, dfs_downloads, dfs_comments, dfs_fans, dfs_soundcloud

'''
Getting feature matrix for timeseries by taking log(abs(diff(total)))
@params: filtered: dict of filtered NBS data, media: type of social media platform 
@return: featuredf: dataframe (rows: artists, cols: plays, downloads, comments)
'''
def getwhole_absvar(filtered, media):
    
    if media == 'Twitter':
        plays, dwn, comment, fans, lists, whole = SCcreating_dfs(filtered)
    else:
        plays, dwn, comment, fans, whole = SCcreating_dfs(filtered)
        
    plays_df = getMovement(plays, 'plays').mean()
    dwn_df = getMovement(dwn, 'downloads').mean()
    comment_df = getMovement(comment, 'comment').mean()
    
#     lists_df = getAvgFeat(getMovement(lists))
    featuredf = pd.concat([plays_df, dwn_df, comment_df], axis = 1)
    featuredf.columns = ['plays', 'downloads', 'comments']
    return featuredf 

def get_linearregresparams(plays_df):
    linear_results = dict()
    for index, vals in plays_df.iterrows():
        model = LinearRegression()
        model = model.fit(np.arange(len(vals.values))[:,np.newaxis], vals.values)
        linear_results[index] = (model.coef_, model.intercept_)
    return linear_results

if if __name__ == '__main__':
    engine = create_engine('postgresql://dubT:!@localhost:5432/nebulae')
    Cnbs_data = pickle.load(open('../converted_nbs.pkl', 'r'))
    NCnbs_data = pickle.load(open('../NBS_noncovert.pkl', 'r'))
    emerge_artists = pd.read_sql('billboard_emerge', engine)
    main()