# FlightDelayPredictor
## MSCI 446

### WeatherData.py: 
For each origin and destination airport, we found their respective departure time and arrival time from cleaned_flight_info.csv and added the weather data for them through querying the details from the weather api (https://archive-api.open-meteo.com/v1/archive). After, we parsed the respective flight details and its weather details on one row in the excel file. To run the script, ensure you have the cleaned_flight_info.csv in the same directory (stores the flight details) as this script and adjust the starting row and ending row in append_weather_to_flights(start_row, end_row) which allows you to configure which rows of flight info you want to parse with weather data. It will output the combined data into cleaned_flight_info.csv which we will use to train our models. 

### Lasoo.ipynb:
-Read data from complete_flight_info_and_weather_data.csv file
-Cleanse data by removing origin/dest, converting TRUE/FALSE to boolean, converting flight date to year/month/day
-Split training, test data and trained lasso model
-Manually tested with different alpha parameters
-Output the MSE, MAE, R2, and the selected predictors after executing predict on test set

### LinearRegression_.ipynb:
-Read data from complete_flight_info_and_weather_data.csv file
-Cleanse data by removing origin/dest, converting TRUE/FALSE to boolean, converting flight date to year/month/day
-Split training, test data and trained Linear Regression Model
-Manually tested with different subsets of predictors after running the different subset selection algorithms 
-Output the MSE, MAE, R2, and the selected predictors after executing predict on test set

### Svr.ipynb:
-Read data from complete_flight_info_and_weather_data.csv file
-Cleanse data by removing origin/dest, converting TRUE/FALSE to boolean, converting flight date to year/month/day
-Split training, test data and trained Linear SVR model
-Manually tested with different kernels
-Output the MSE, MAE, R2, and the selected predictors after executing predict on test set

### Flight_data_preparation.ipynb : 
-combining data from multiple data files and dropping unnecessary columns(features)

### Forward_subset_selection.ipynb: 
-Read data from “complete_flight_info_and weather_data.csv”
-Implements forward feature selection for linear regression
-Iteratively adds features that improve the cross-validated R-squared score
-Returns the selected features up to a specified maximum

### Best_subset_selection.ipynb: 
-Read data from “complete_flight_info_and weather_data.csv”
-Denote a null model with no predictors
-Fit all p choose k models that contains exactly k predictors
-Pick the best among the p choose k models call it Mk. Best is defined a having the smallest RSS and largest R^2
-Calculates minimum test MSE, test R2, and test MAPE

### tree_bagging.ipynb: 
-randomly creates multiple training sets from the data from “complete_flight_info_and weather_data.csv” data file and builds a separate decision tree for each. Each model is then used to predict on the test set, lastly, the average of the results is taken as the prediction of the tree-based model. 
-Calculates minimum test MSE, test R2, and test MAPE

### Decision_tree.ipynb:
-Trains a decision tree regression model with varying maximum depths (1 to 29)
-Calculates and stores the mean squared error (MSE), R-squared (R2), and mean absolute percentage error (MAPE) for both training and test sets
-Finds the maximum depth that yields the minimum test MSE
-Prints the optimized model's maximum depth, test MSE, test R2, and test MAPE

### Random_forest.ipynb:
-Performs hyperparameter tuning for a Random Forest Regressor model using GridSearchCV
-Tunes the max_depth and n_estimators hyperparameters using a grid of values
-Evaluates the best model on the test set using metrics like MSE, R-squared, and MAPE
-Prints the best hyperparameters and evaluation metrics for the tuned model

### Ridge.ipynb:
-Read data from complete_flight_info_and_weather_data.csv file
-Cleanse data by removing origin/dest, converting TRUE/FALSE to boolean, converting flight date to year/month/day
-Split training, test data and trained ridge model
-Manually tested with different alpha parameters, best MSE found at alpha = 1
-Output the MSE, MAE, R2, and the selected predictors after executing predict on test set

### Quadratic.ipynb:
-Read data from complete_flight_info_and_weather_data.csv file
-Cleanse data by removing origin/dest, converting TRUE/FALSE to boolean, converting flight date to year/month/day
-Split training, test data
-Create new features based on existing one using polynomial features
-Manually tested with different degree parameters
-Output the MSE, MAE, R2, and the selected predictors after executing predict on test set

### backward_subset_selection.ipynb: 
Read data from “complete_flight_info_and weather_data.csv”
Implements backward feature selection for linear regression
Iteratively adds features that improve the cross-validated R-squared score
Returns the selected features

### boosting.ipynb: 
Randomly generates multiple training sets from the data from “complete_flight_info_and weather_data.csv” data file and Each model is then used to predict on the test set, lastly, the average of the results is taken as the prediction of the gradient boosting model. 
Calculates minimum test MSE, test R2, and test MAPE