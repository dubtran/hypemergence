import pandas as pd
import numpy as np 
from sklearn.linear_model import LogisticRegression as lr
from sklearn.cross_validation import KFold, train_test_split
from sklearn.metrics import auc, f1_score, accuracy_score, precision_score, recall_score, roc_curve
from collections import Counter
from sklearn.ensemble import RandomForestClassifier as RF
from sqlalchemy import create_engine
import sklearn.svm as svm

engine = create_engine('postgresql://dubT:unicorn!@localhost:5432/nebulae')

if __name__ == '__main__':
	
	featuredf = pd.read_sql('soundcloud_finalft', engine)

	x = featuredf_lin[['plays', 'discovery', 'familiarity', 'hottness', 'p_rising', 'lin_coef']].replace([np.inf, -np.inf], np.nan).fillna(0)
	y = featuredf_lin['b_emerging']
	
	tuned_parameters = [{'criterion':['gini','entropy'], 'max_features': ['sqrt', 'log2'], 'oob_score': [True, False]}]
	rf = GridSearchCV( RF(min_samples_split=1, compute_importances=False, n_jobs=-1), tuned_parameters, cv=2, verbose=2 ).fit(x, y.fillna(0))
	rf.best_estimator_.fit(x,y)
	



