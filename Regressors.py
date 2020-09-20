# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 14:44:56 2020

@author: karby
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score


class Regressor:
    def __init__(self, independent, dependent):
        self.X = independent
        self.y = dependent
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size = 0.2, random_state =  0)
    
    def decision_tree(self):
        # Train the data
        from sklearn.tree import DecisionTreeRegressor
        regressor = DecisionTreeRegressor(random_state = 0)
        regressor.fit(self.X_train, self.y_train)
        
        # Predict the data
        # I do all of the reshaping so the result matrix is a 2 row matrix
        # With the actual results on top and our guesses on bottom
        y_pred = regressor.predict(self.X_test)
        np.set_printoptions(precision=2)
        pred_reshape = y_pred.reshape(1, len(y_pred))
        test_reshape = self.y_test.reshape(1, len(self.y_test))
        results = np.concatenate((test_reshape, pred_reshape))
        
        # Evaluating the model performance using R
        print(r2_score(self.y_test, y_pred)) 
        
        
    def polynomial(self):
        # Training the data
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression
        poly_reg = PolynomialFeatures(degree = 4)
        X_poly = poly_reg.fit_transform(self.X_train)
        regressor = LinearRegression()
        regressor.fit(X_poly, self.y_train)

        # Predicting the results
        y_pred = regressor.predict(poly_reg.transform(self.X_test))
        np.set_printoptions(precision=2)
        pred_reshape = y_pred.reshape(1, len(y_pred))
        test_reshape = self.y_test.reshape(1, len(self.y_test))
        results = np.concatenate((test_reshape, pred_reshape))
        
        # Evaluating the model performance using R2
        print(r2_score(self.y_test, y_pred))
        
    
    def random_forrest(self):
        from sklearn.ensemble import RandomForestRegressor
        regressor = RandomForestRegressor(n_estimators = 10, random_state = 0)
        regressor.fit(self.X_train, self.y_train)
        

        # Predicting the results
        y_pred = regressor.predict(self.X_test)
        np.set_printoptions(precision=2)
        pred_reshape = y_pred.reshape(1, len(y_pred))
        test_reshape = self.y_test.reshape(1, len(self.y_test))
        results = np.concatenate((test_reshape, pred_reshape))
        
        # Evaluating the model performance using R2
        print(r2_score(self.y_test, y_pred))
        
        
    def suport_vector(self):
        # You must use feature scaling for SVR
        from sklearn.preprocessing import StandardScaler
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        X_train = sc_x.fit_transform(self.X_train)
        y_train = sc_y.fit_transform(self.y_train)

        # Training the SVR model on the data
        from sklearn.svm import SVR
        regressor = SVR(kernel = 'rbf')
        regressor.fit(X_train, y_train)
        
        # Predicting the data
        y_pred = sc_y.inverse_transform(regressor.predict(sc_x.transform(self.X_test)))
        np.set_printoptions(precision=2)
        pred_reshape = y_pred.reshape(1, len(y_pred))
        test_reshape = self.y_test.reshape(1, len(self.y_test))
        results = np.concatenate((test_reshape, pred_reshape))
        
        # Evaluating the model performance using R2
        print(r2_score(self.y_test, y_pred))
        
        
    def multiple_linear(self):
        # Train the data
        from sklearn.linear_model import LinearRegression
        regressor = LinearRegression()
        regressor.fit(self.X_train, self.y_train)
        
        # Predicting the test results
        y_pred = regressor.predict(self.X_test)
        np.set_printoptions(precision=2)
        pred_reshape = y_pred.reshape(1, len(y_pred))
        test_reshape = self.y_test.reshape(1, len(self.y_test))
        results = np.concatenate((test_reshape, pred_reshape))
        
        # Evaluating the model performance using R2
        print(r2_score(self.y_test, y_pred))
