# Model Evaluation and Selection Guide

This guide helps you understand, interpret, and compare the machine learning models in the Expense Predictor system.

## Table of Contents

- [Understanding the Models](#understanding-the-models)
- [Interpreting Performance Metrics](#interpreting-performance-metrics)
- [Model Comparison](#model-comparison)
- [Choosing the Right Model](#choosing-the-right-model)
- [Hyperparameter Tuning](#hyperparameter-tuning)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Best Practices](#best-practices)

## Understanding the Models

The Expense Predictor uses four regression models. Each has different strengths and is suitable for different types of transaction patterns.

### 1. Linear Regression

**What it does**: Finds the best straight-line relationship between date features and transaction amounts.

**Strengths**:
- ✅ Fast training and prediction
- ✅ Easy to understand and interpret
- ✅ Works well for stable, predictable patterns
- ✅ No hyperparameters to tune

**Weaknesses**:
- ❌ Cannot capture complex patterns
- ❌ Assumes linear relationships
- ❌ Sensitive to outliers

**Best for**:
- Regular monthly bills (rent, subscriptions)
- Stable, predictable expenses
- Quick baseline predictions

**Example Use Case**: Predicting monthly rent or insurance payments that occur on the same day each month with the same amount.

### 2. Decision Tree

**What it does**: Creates a tree of decision rules based on date features (e.g., "If day of month > 15 and weekday = Monday, predict $150").

**Strengths**:
- ✅ Captures non-linear patterns
- ✅ Interpretable decision rules
- ✅ Handles feature interactions automatically
- ✅ Fast prediction

**Weaknesses**:
- ❌ Prone to overfitting
- ❌ Can be unstable (small data changes → big tree changes)
- ❌ Usually less accurate than ensemble methods

**Best for**:
- Understanding which factors drive predictions
- Datasets with clear categorical patterns (weekday vs weekend)
- When you need explainable predictions

**Example Use Case**: Identifying that you spend more on weekends, at month-end, or during specific months.

### 3. Random Forest

**What it does**: Builds many decision trees and averages their predictions to reduce overfitting.

**Strengths**:
- ✅ More accurate than single decision tree
- ✅ Resistant to overfitting
- ✅ Handles outliers well
- ✅ Provides feature importance rankings

**Weaknesses**:
- ❌ Slower training than single tree
- ❌ Less interpretable than single tree
- ❌ Larger model size (100 trees)

**Best for**:
- Production deployments
- General-purpose predictions
- When you have irregular transaction patterns

**Example Use Case**: Predicting variable personal expenses with a mix of regular and irregular transactions.

### 4. Gradient Boosting

**What it does**: Builds trees sequentially, where each tree corrects the errors of previous trees.

**Strengths**:
- ✅ Often the most accurate model
- ✅ Excellent for complex patterns
- ✅ Handles missing data well

**Weaknesses**:
- ❌ Slowest training time
- ❌ Requires careful tuning
- ❌ Can overfit if not properly configured
- ❌ Least interpretable

**Best for**:
- Critical financial forecasting
- When accuracy is paramount
- Complex, variable transaction patterns

**Example Use Case**: Business expense forecasting where accuracy directly impacts budget planning.

## Interpreting Performance Metrics

The system reports three metrics for each model. Understanding these helps you evaluate model performance.

### RMSE (Root Mean Squared Error)

**What it measures**: Average prediction error in the same units as your transaction amounts.

**Interpretation**:
- Lower is better (0 = perfect)
- Units: Same as your transaction amounts (e.g., dollars, euros)
- Penalizes large errors more heavily

**Example**:
```
RMSE = 25.50
```
- On average, predictions are off by ~$25.50
- Some predictions might be off by much more (RMSE emphasizes large errors)

**When to use**:
- When large errors are particularly problematic
- Comparing models (lower RMSE = better)

**Typical ranges**:
- **Excellent**: RMSE < 10% of average transaction amount
- **Good**: RMSE < 20% of average transaction amount
- **Fair**: RMSE < 30% of average transaction amount
- **Poor**: RMSE > 30% of average transaction amount

### MAE (Mean Absolute Error)

**What it measures**: Average absolute prediction error.

**Interpretation**:
- Lower is better (0 = perfect)
- Units: Same as your transaction amounts
- More robust to outliers than RMSE

**Example**:
```
MAE = 18.75
```
- On average, predictions are off by $18.75 (up or down)
- More interpretable than RMSE

**When to use**:
- When you want an intuitive measure of average error
- When outliers shouldn't dominate the metric

**Comparison to RMSE**:
- MAE < RMSE: Some predictions have large errors
- MAE ≈ RMSE: Errors are relatively consistent
- MAE >> RMSE: This shouldn't happen (data issue)

### R² Score (Coefficient of Determination)

**What it measures**: Proportion of variance in transaction amounts explained by the model.

**Interpretation**:
- Range: -∞ to 1.0
- 1.0 = Perfect predictions (100% variance explained)
- 0.5 = Model explains 50% of variance
- 0.0 = Model as good as predicting the average
- Negative = Model worse than predicting the average

**Example**:
```
R² = 0.75
```
- Model explains 75% of the variation in transaction amounts
- 25% is unexplained (random variation, missing features)

**Interpretation guide**:
- **Excellent**: R² > 0.9 (90%+ variance explained)
- **Good**: R² = 0.7-0.9 (70-90% variance explained)
- **Fair**: R² = 0.5-0.7 (50-70% variance explained)
- **Poor**: R² < 0.5 (<50% variance explained)
- **Very Poor**: R² < 0 (worse than predicting average)

**When to use**:
- Comparing models (higher R² = better)
- Understanding how much patterns exist in your data
- Determining if predictions are reliable

**Important notes**:
- R² alone doesn't tell the full story
- High R² on training data + low R² on test data = overfitting
- Always prioritize test set R² over training set R²

### MedAE (Median Absolute Error)

**What it measures**: Median absolute prediction error (robust to outliers).

**Interpretation**:
- Lower is better (0 = perfect)
- Units: Same as your transaction amounts
- Represents a "typical" error without being skewed by outliers

**When to use**:
- When outliers dominate MAE/RMSE
- When you want a more stable, typical error measure

### SMAPE (Symmetric Mean Absolute Percentage Error)

**What it measures**: Percentage error that is symmetric and less sensitive to zeros.

**Interpretation**:
- Lower is better (0% = perfect)
- Units: Percentage
- Useful for comparing accuracy across different scales

**When to use**:
- When you want a scale-free metric
- When data includes small or zero values

### Error Percentiles (P50/P75/P90)

**What they measure**: Distribution of absolute errors.

**Interpretation**:
- P50: Typical error (median)
- P75: Error level for 75% of predictions
- P90: Worst-case error for most predictions

**When to use**:
- When you want to understand tail risk in forecasts
- When setting practical error bounds for budgeting

## Model Comparison

### Reading the Log Output

After running the script, check your log file for output like this:

```
Model: Linear Regression
Training Set Performance:
  RMSE: 22.15
  MAE: 18.30
  R²: 0.6543
Test Set Performance:
  RMSE: 24.50
  MAE: 19.75
  R²: 0.6120

Model: Random Forest
Training Set Performance:
  RMSE: 12.80
  MAE: 10.25
  R²: 0.8745
Test Set Performance:
  RMSE: 18.90
  MAE: 15.40
  R²: 0.7650
```

### What to Look For

#### 1. Test Set Performance (Most Important)

**Focus on test set metrics**, not training set. Test set represents real-world performance on unseen data.

**Good signs**:
- Low RMSE and MAE on test set
- High R² on test set (>0.7)
- Metrics similar to or slightly worse than training set

**Bad signs**:
- High RMSE and MAE on test set
- Low or negative R² on test set
- Huge gap between training and test metrics (overfitting)

#### 2. Overfitting Detection

**Overfitting** = Model memorizes training data but fails on new data

**Signs of overfitting**:
```
Training R²: 0.95  |  Test R²: 0.55  ← Big gap (0.40)
Training RMSE: 8   |  Test RMSE: 35  ← Test much worse
```

**Healthy model**:
```
Training R²: 0.78  |  Test R²: 0.74  ← Small gap (0.04)
Training RMSE: 15  |  Test RMSE: 18  ← Reasonable difference
```

**Acceptable gaps**:
- R² difference: <0.10 (excellent), <0.15 (good), >0.20 (overfitting)
- RMSE ratio (test/train): <1.2 (excellent), <1.5 (good), >2.0 (overfitting)

#### 3. Model Ranking

Compare **test set R²** scores to rank models:

```
1. Gradient Boosting: R² = 0.82  ← Best
2. Random Forest:     R² = 0.78  ← Second
3. Decision Tree:     R² = 0.65  ← Third
4. Linear Regression: R² = 0.61  ← Baseline
```

Use the predictions from the best-performing model (highest test R²).

### Comparing Against Baselines

Baseline forecasts (naive last value, rolling means, seasonal naive) are logged and
ranked alongside ML models. If a baseline consistently outperforms a complex model,
it is a signal to review data quality, feature engineering, or model settings.

## Choosing the Right Model

### Decision Framework

Use this flowchart to choose the appropriate model:

```
Do you need to explain predictions?
│
├─ YES → Use Decision Tree
│         (interpretable rules)
│
└─ NO → Is accuracy critical?
         │
         ├─ YES → Use Gradient Boosting
         │         (highest accuracy)
         │
         └─ NO → Do you have irregular patterns?
                  │
                  ├─ YES → Use Random Forest
                  │         (robust, general purpose)
                  │
                  └─ NO → Use Linear Regression
                            (simple, stable patterns)
```

### Scenario-Based Recommendations

#### Scenario 1: Regular Monthly Bills

**Pattern**: Same amount, same date every month (rent, subscriptions)

**Recommended Model**: Linear Regression
- Fast and simple
- Handles regular patterns well
- Easy to understand

**Expected Performance**: R² > 0.8

#### Scenario 2: Variable Personal Expenses

**Pattern**: Irregular amounts, varies by day/week/month

**Recommended Model**: Random Forest or Gradient Boosting
- Captures complex patterns
- Resistant to outliers
- Good generalization

**Expected Performance**: R² = 0.6-0.8

#### Scenario 3: Business Expense Forecasting

**Pattern**: Mix of regular and irregular, seasonal patterns

**Recommended Model**: Gradient Boosting
- Highest accuracy
- Handles complexity well
- Worth the extra training time

**Expected Performance**: R² = 0.7-0.85

#### Scenario 4: Learning/Experimentation

**Pattern**: Want to understand spending patterns

**Recommended Model**: Decision Tree
- Interpretable rules
- Shows which factors matter
- Educational value

**Expected Performance**: R² = 0.6-0.75

### Quick Comparison Table

| Criterion | Linear Reg | Decision Tree | Random Forest | Gradient Boost |
|-----------|-----------|---------------|---------------|----------------|
| **Speed** | ⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| **Accuracy** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Interpretability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Overfitting Risk** | Low | High | Low | Medium |
| **Regular Patterns** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Complex Patterns** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Hyperparameter Tuning

If your models aren't performing well, try tuning hyperparameters in `config.yaml`.
Tree-based models can also use constrained, time-series-aware tuning that persists
best parameters to a JSON report for reuse on subsequent runs.

### When to Tune

**Signs you need tuning**:
- Large gap between training and test performance (overfitting)
- Poor test set performance (R² < 0.5)
- Predictions don't match your expectations

### Decision Tree Tuning

Edit `config.yaml`:

```yaml
decision_tree:
  max_depth: 5              # ← Start here
  min_samples_split: 10     # ← Then try this
  min_samples_leaf: 5
  ccp_alpha: 0.01
  random_state: 42
```

**If overfitting** (training R² >> test R²):
- ↓ Decrease `max_depth` (try 3 or 4)
- ↑ Increase `min_samples_split` (try 20 or 30)
- ↑ Increase `min_samples_leaf` (try 10 or 15)
- ↑ Increase `ccp_alpha` (try 0.02 or 0.03)

**If underfitting** (both training and test R² low):
- ↑ Increase `max_depth` (try 7 or 10)
- ↓ Decrease `min_samples_split` (try 5)
- ↓ Decrease `min_samples_leaf` (try 2)
- ↓ Decrease `ccp_alpha` (try 0.005)

### Random Forest Tuning

```yaml
random_forest:
  n_estimators: 100         # ← More trees = better (but slower)
  max_depth: 10             # ← Control complexity
  min_samples_split: 10
  min_samples_leaf: 5
  max_features: "sqrt"
  ccp_alpha: 0.01
  random_state: 42
```

**If overfitting**:
- ↓ Decrease `max_depth` (try 7 or 8)
- ↑ Increase `min_samples_leaf` (try 10)
- ↑ Increase `ccp_alpha` (try 0.02)

**If underfitting**:
- ↑ Increase `n_estimators` (try 200 or 300)
- ↑ Increase `max_depth` (try 15 or 20)
- Change `max_features` to "log2" or None

**Performance vs Speed**:
- More `n_estimators` = better predictions but slower
- 50 trees: Fast, decent accuracy
- 100 trees: Good balance (default)
- 200+ trees: Marginal improvement, much slower

### Gradient Boosting Tuning

```yaml
gradient_boosting:
  n_estimators: 100         # ← Number of boosting stages
  learning_rate: 0.1        # ← Step size (smaller = more careful)
  max_depth: 5              # ← Keep shallow for boosting
  min_samples_split: 10
  min_samples_leaf: 5
  max_features: "sqrt"
  random_state: 42
```

**If overfitting**:
- ↓ Decrease `learning_rate` (try 0.05 or 0.01)
- ↑ Increase `n_estimators` (compensate for lower learning rate)
- ↓ Decrease `max_depth` (try 3 or 4)
- ↑ Increase `min_samples_leaf` (try 10)

**If underfitting**:
- ↑ Increase `learning_rate` (try 0.15 or 0.2)
- ↑ Increase `n_estimators` (try 200)
- ↑ Increase `max_depth` (try 6 or 7)

**Learning Rate Trade-offs**:
- High learning rate (0.2+): Fast training, risk of overfitting
- Medium learning rate (0.1): Good balance (default)
- Low learning rate (0.01-0.05): Better generalization, needs more estimators

### Tuning Strategy

1. **Start with defaults**: Run once with default config
2. **Identify the problem**: Overfitting or underfitting?
3. **Make one change at a time**: Change one parameter, test, observe
4. **Track results**: Keep notes on parameter combinations and results
5. **Use test set performance**: Only trust test set metrics

**Example tuning log**:
```
Config 1 (defaults): Test R² = 0.72, Gap = 0.18 (overfitting)
Config 2 (max_depth=3): Test R² = 0.68, Gap = 0.08 (better!)
Config 3 (+ min_samples_leaf=10): Test R² = 0.71, Gap = 0.06 (even better!)
→ Use Config 3
```

## Common Issues and Solutions

### Issue 1: All Models Perform Poorly

**Symptoms**: R² < 0.3 for all models, high RMSE

**Possible Causes**:
- Not enough historical data
- Data is too random (no patterns)
- Missing important features (e.g., categories, merchant info)

**Solutions**:
1. Collect more historical data (ideally 3-6 months)
2. Check if transaction patterns actually exist
3. Consider if expense prediction is feasible for your data

### Issue 2: Training Good, Test Poor (Overfitting)

**Symptoms**: Training R² > 0.9, Test R² < 0.6

**Solutions**:
1. Reduce model complexity (see tuning above)
2. Get more training data
3. Use simpler model (Linear Regression or Decision Tree with low depth)

### Issue 3: Both Training and Test Poor (Underfitting)

**Symptoms**: Training R² < 0.5, Test R² < 0.5

**Solutions**:
1. Increase model complexity
2. Check data quality (missing values, errors)
3. Add more features (future enhancement)

### Issue 4: Negative R² Score

**Symptoms**: R² < 0 on test set

**Meaning**: Model is worse than just predicting the average

**Solutions**:
1. Check for data leakage or errors
2. Verify data preprocessing is correct
3. Try simpler model (Linear Regression)
4. Check if you have enough data

### Issue 5: Predictions Don't Make Sense

**Symptoms**: Predictions are negative or unrealistically high

**Possible Causes**:
- Model extrapolating beyond training data range
- Outliers in training data
- Data quality issues

**Solutions**:
1. Check training data for outliers
2. Clip predictions to reasonable range
3. Add domain constraints (e.g., min=0 for expenses)

## Best Practices

### 1. Always Compare Train and Test Performance

```
✓ Good: Check both metrics
✗ Bad: Only look at training performance
```

Training performance can be misleading (overfitting).

### 2. Use Multiple Models

```
✓ Good: Compare all 4 models, choose best
✗ Bad: Always use the same model
```

Different data patterns favor different models.

### 3. Monitor for Overfitting

```
✓ Good: Watch for large train/test gaps
✗ Bad: Celebrate high training R² without checking test
```

Overfitting is the most common problem.

### 4. Tune Conservatively

```
✓ Good: Small parameter changes, test each
✗ Bad: Change multiple parameters at once
```

Can't tell what helps if you change too much.

### 5. Use Appropriate Metrics

```
✓ Good: Consider RMSE, MAE, and R² together
✗ Bad: Focus only on R²
```

Each metric provides different insights.

### 6. Keep Historical Data

```
✓ Good: Accumulate more data over time
✗ Bad: Delete old transactions
```

More data = better predictions.

### 7. Validate Predictions

```
✓ Good: Compare predictions to actual outcomes
✗ Bad: Blindly trust predictions
```

Track prediction accuracy over time.

### 8. Document Your Tuning

```
✓ Good: Keep notes on config changes and results
✗ Bad: Randomly change parameters
```

Helps you learn what works for your data.

## Example Workflow

### Step 1: Run with Defaults

```bash
python model_runner.py --data_file trandata.csv
```

### Step 2: Check Log File

```bash
cat logs/model_runner.py_*.log | grep "R²"
```

### Step 3: Identify Best Model

Look for highest test set R²:
```
Linear Regression: Test R² = 0.61
Decision Tree: Test R² = 0.68
Random Forest: Test R² = 0.76  ← Best
Gradient Boosting: Test R² = 0.74
```

### Step 4: Check for Overfitting

```
Random Forest:
Training R² = 0.82
Test R² = 0.76
Gap = 0.06  ← Good! (< 0.10)
```

### Step 5: Use Best Model Predictions

```bash
# Use the Random Forest predictions
cp future_predictions_random_forest.csv my_forecast.csv
```

### Step 6: (Optional) Tune if Needed

If overfitting or poor performance, edit `config.yaml` and rerun.

## Additional Resources

- **ARCHITECTURE.md**: Detailed model selection rationale
- **README.md**: Usage examples and troubleshooting
- **config.yaml**: Hyperparameter configuration file
- **Log Files**: Detailed performance metrics

## Questions?

For model evaluation questions or issues, please open an issue on the [GitHub repository](https://github.com/manoj-bhaskaran/expense-predictor/issues).
