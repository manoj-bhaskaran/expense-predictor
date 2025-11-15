# Architecture Documentation

This document describes the system architecture, design decisions, and technical implementation details of the Expense Predictor.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Design](#architecture-design)
- [Model Selection Rationale](#model-selection-rationale)
- [Feature Engineering](#feature-engineering)
- [Data Flow](#data-flow)
- [Performance Benchmarking](#performance-benchmarking)
- [Design Decisions](#design-decisions)

## System Overview

The Expense Predictor is a machine learning-based forecasting system that analyzes historical transaction data to predict future expenses. The system uses a multi-model approach, training four different regression algorithms and allowing users to compare their performance.

### Key Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Expense Predictor                        │
├─────────────────────────────────────────────────────────────┤
│  Input Layer                                                 │
│  ├── CSV Parser (trandata.csv)                              │
│  └── Excel Parser (bank_statement.xls/xlsx)                 │
├─────────────────────────────────────────────────────────────┤
│  Validation Layer                                            │
│  ├── File Validation (security.py)                          │
│  ├── Column Validation (helpers.py)                         │
│  └── Date Range Validation (helpers.py)                     │
├─────────────────────────────────────────────────────────────┤
│  Preprocessing Layer                                         │
│  ├── Data Cleaning (duplicates, missing values)             │
│  ├── Date Normalization                                     │
│  ├── Date Range Completion (fill missing dates)             │
│  └── Feature Engineering                                    │
├─────────────────────────────────────────────────────────────┤
│  Model Layer                                                 │
│  ├── Linear Regression                                      │
│  ├── Decision Tree Regressor                                │
│  ├── Random Forest Regressor                                │
│  └── Gradient Boosting Regressor                            │
├─────────────────────────────────────────────────────────────┤
│  Evaluation Layer                                            │
│  ├── Train/Test Split (80/20)                               │
│  ├── RMSE Calculation                                       │
│  ├── MAE Calculation                                        │
│  └── R² Score Calculation                                   │
├─────────────────────────────────────────────────────────────┤
│  Output Layer                                                │
│  ├── Prediction Generation                                  │
│  ├── CSV Sanitization (injection prevention)                │
│  └── File Writing (with backup)                             │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Design

### Modular Design

The system follows a modular architecture with clear separation of concerns:

1. **model_runner.py** - Main orchestrator
   - Entry point and CLI argument parsing
   - Model training and evaluation workflow
   - Prediction generation and output

2. **helpers.py** - Data processing utilities
   - Input validation functions
   - Data preprocessing and cleaning
   - Feature engineering
   - Prediction writing

3. **security.py** - Security utilities
   - Path validation and sanitization
   - File extension validation
   - CSV injection prevention
   - Backup creation

4. **config.py** - Configuration management
   - YAML configuration loading
   - Default values fallback
   - Configuration validation

### Design Patterns

**Separation of Concerns**: Each module has a single, well-defined responsibility.

**Dependency Injection**: Logger and configuration are passed as parameters, allowing for flexible testing and configuration.

**Fail-Fast**: Validation happens early in the pipeline to provide immediate feedback.

**Defensive Programming**: All user inputs are validated and sanitized before use.

## Model Selection Rationale

The system implements four different regression algorithms, each with distinct characteristics:

### 1. Linear Regression

**Purpose**: Baseline model for comparison

**Rationale**:
- Simplest possible model - establishes performance baseline
- No hyperparameters to tune
- Fast training and prediction
- Easy to interpret results
- Good for detecting linear trends in transaction patterns

**When to Use**:
- When transaction patterns are relatively stable
- For quick baseline predictions
- When interpretability is more important than accuracy

**Limitations**:
- Cannot capture non-linear patterns
- Sensitive to outliers
- Assumes linear relationship between features and target

### 2. Decision Tree Regressor

**Purpose**: Non-linear pattern detection with interpretability

**Rationale**:
- Can capture non-linear relationships in transaction data
- Handles feature interactions automatically
- No assumptions about data distribution
- Interpretable decision rules
- Fast prediction time

**Hyperparameters**:
- `max_depth=5`: Limits tree depth to prevent overfitting
- `min_samples_split=10`: Requires 10 samples to split a node
- `min_samples_leaf=5`: Requires 5 samples in each leaf
- `ccp_alpha=0.01`: Cost complexity pruning for regularization

**When to Use**:
- When you need to understand the decision-making process
- For datasets with clear categorical patterns (e.g., weekday vs weekend spending)
- When speed is important

**Limitations**:
- Prone to overfitting without pruning
- Can be unstable (small data changes cause big tree changes)
- Less accurate than ensemble methods

### 3. Random Forest Regressor

**Purpose**: Robust ensemble predictions with reduced variance

**Rationale**:
- Ensemble of decision trees reduces overfitting
- Handles missing data and outliers well
- Provides feature importance rankings
- More stable than single decision trees
- Good generalization performance

**Hyperparameters**:
- `n_estimators=100`: 100 trees for robust predictions
- `max_depth=10`: Deeper trees than single tree (ensemble reduces overfitting)
- `max_features="sqrt"`: Random feature selection for diversity
- `min_samples_split=10`: Conservative splitting
- `min_samples_leaf=5`: Prevents tiny leaves

**When to Use**:
- For production deployments requiring reliability
- When you have sufficient data (hundreds of samples)
- When you need feature importance insights

**Limitations**:
- Slower training than single trees
- Less interpretable than decision trees
- Larger model size (100 trees)

### 4. Gradient Boosting Regressor

**Purpose**: Highest accuracy through iterative improvement

**Rationale**:
- Builds trees sequentially, each correcting previous errors
- Often achieves best predictive performance
- Handles complex patterns effectively
- Good for competitions and high-stakes predictions

**Hyperparameters**:
- `n_estimators=100`: 100 boosting iterations
- `learning_rate=0.1`: Moderate learning rate for stability
- `max_depth=5`: Shallow trees (boosting works well with weak learners)
- `max_features="sqrt"`: Feature randomization
- `min_samples_split=10`: Conservative splitting

**When to Use**:
- When you need the best possible predictions
- When you have clean, well-prepared data
- For critical financial forecasting

**Limitations**:
- Slowest training time
- Requires careful hyperparameter tuning
- Can overfit if not properly regularized
- Less interpretable

## Feature Engineering

### Feature Selection Rationale

The system creates time-based features from transaction dates:

#### 1. Day of the Week (Categorical → One-Hot Encoded)

**Why**: Transaction patterns often vary by day of week
- Weekdays (Mon-Fri): Regular expenses (commute, lunch, etc.)
- Weekends (Sat-Sun): Different spending patterns (entertainment, dining)

**Implementation**: One-hot encoding with 6 dummy variables (drop first to avoid multicollinearity)

**Impact**: Captures weekly cyclical patterns in spending

#### 2. Month (Numeric: 1-12)

**Why**: Monthly patterns in expenses
- Regular monthly bills (rent, subscriptions)
- Seasonal variations (holidays, vacations)
- Pay cycle effects (spending after payday)

**Implementation**: Direct numeric encoding preserves ordinal relationship

**Impact**: Captures yearly cyclical patterns and seasonality

#### 3. Day of the Month (Numeric: 1-31)

**Why**: Intra-month spending patterns
- Beginning of month: Bill payments, rent
- Mid-month: Regular spending
- End of month: Pre-payday spending patterns

**Implementation**: Direct numeric encoding (1-31)

**Impact**: Captures monthly spending cycles

### Features NOT Included

**Historical Lag Features** (e.g., previous day's amount):
- Not included to keep model simple
- Would require more complex data handling
- Current features capture patterns adequately
- Could be added in future versions

**Moving Averages**:
- Not included in current version
- Would smooth out daily variations
- Potential future enhancement

**Category/Merchant Information**:
- Not available in current data format
- Would significantly improve predictions
- Requires more detailed transaction data

## Data Flow

### 1. Input Stage

```
CSV File (trandata.csv)          Excel File (bank_statement.xlsx)
        ↓                                       ↓
  validate_csv_file()              validate_excel_file()
        ↓                                       ↓
   Read CSV                              Read Excel
        ↓                                       ↓
        └──────────────┬────────────────────────┘
                       ↓
              Merge on Date
```

### 2. Preprocessing Stage

```
Raw Data
    ↓
Remove Duplicates (keep last)
    ↓
Convert Dates to datetime
    ↓
validate_date_range()
    ↓
Create Complete Date Range (earliest → yesterday)
    ↓
Fill Missing Dates with 0 amount
    ↓
Feature Engineering
    ├── Extract Day of Week → One-Hot Encode (6 columns)
    ├── Extract Month → Numeric (1-12)
    └── Extract Day of Month → Numeric (1-31)
    ↓
Final Feature Matrix (8 features)
```

### 3. Training Stage

```
Preprocessed Data
    ↓
Train/Test Split (80/20, shuffle=False)
    ↓
    ├── Training Set (80%)
    │       ↓
    │   Train 4 Models (parallel)
    │   ├── Linear Regression
    │   ├── Decision Tree
    │   ├── Random Forest
    │   └── Gradient Boosting
    │       ↓
    │   Evaluate on Training Set
    │       ↓
    └── Test Set (20%)
            ↓
        Evaluate on Test Set
        ├── Calculate RMSE
        ├── Calculate MAE
        └── Calculate R²
```

### 4. Prediction Stage

```
Trained Models + Future Date
    ↓
prepare_future_dates()
    ↓
Generate Future Date Range
    ↓
Extract Same Features (Day of Week, Month, Day of Month)
    ↓
One-Hot Encode Day of Week
    ↓
Align Features with Training Data
    ↓
Generate Predictions (all 4 models)
    ↓
sanitize_dataframe_for_csv()
    ↓
create_backup() (if file exists)
    ↓
Write Prediction CSVs
```

## Performance Benchmarking

### Evaluation Metrics

#### RMSE (Root Mean Squared Error)
- **What**: Square root of average squared errors
- **Interpretation**: Average prediction error in same units as target
- **Lower is better**: 0 = perfect predictions
- **Sensitivity**: Penalizes large errors more heavily

#### MAE (Mean Absolute Error)
- **What**: Average absolute error
- **Interpretation**: Average deviation from actual values
- **Lower is better**: 0 = perfect predictions
- **Robustness**: Less sensitive to outliers than RMSE

#### R² Score (Coefficient of Determination)
- **What**: Proportion of variance explained
- **Range**: -∞ to 1.0
- **Interpretation**:
  - 1.0 = Perfect predictions
  - 0.0 = Model as good as predicting the mean
  - <0.0 = Model worse than predicting the mean
- **Higher is better**

### Expected Performance Ranges

Performance varies based on data characteristics. Here are typical ranges:

**Simple, Regular Transactions** (e.g., fixed monthly bills):
- Linear Regression: R² = 0.6-0.8, RMSE = low
- Decision Tree: R² = 0.7-0.85, RMSE = moderate
- Random Forest: R² = 0.75-0.9, RMSE = low-moderate
- Gradient Boosting: R² = 0.8-0.95, RMSE = low

**Complex, Variable Transactions** (e.g., irregular personal spending):
- Linear Regression: R² = 0.3-0.5, RMSE = high
- Decision Tree: R² = 0.4-0.6, RMSE = moderate-high
- Random Forest: R² = 0.5-0.7, RMSE = moderate
- Gradient Boosting: R² = 0.6-0.8, RMSE = moderate

**Indicators of Overfitting**:
- Training R² >> Test R² (gap > 0.15)
- Training RMSE << Test RMSE (ratio > 1.5)
- Action: Reduce model complexity (decrease `max_depth`, increase `min_samples_leaf`)

### Benchmarking Process

1. **Baseline**: Linear Regression establishes minimum acceptable performance
2. **Comparison**: Compare complex models against baseline
3. **Overfitting Check**: Compare training vs test metrics
4. **Selection**: Choose model based on:
   - Test set performance (not training)
   - Prediction speed requirements
   - Interpretability needs

## Design Decisions

### Why 80/20 Train/Test Split?

**Rationale**:
- Standard practice in machine learning
- 80% data for training provides sufficient samples
- 20% for testing provides reliable performance estimates
- No shuffle (`shuffle=False`) preserves temporal order
- Temporal split more realistic for time series

### Why No Cross-Validation?

**Current Design**: Simple 80/20 split

**Rationale**:
- Simpler implementation for initial version
- Faster training (no multiple folds)
- Time series data makes cross-validation complex
- Future enhancement opportunity

### Why Multiple Models?

**Rationale**:
- Different models excel with different data patterns
- Users can compare and choose best performer
- Ensemble predictions possible (future enhancement)
- Educational value - understand model differences

### Why No Neural Networks / Deep Learning?

**Rationale**:
- Transaction datasets typically small (<10K samples)
- Deep learning requires large datasets (100K+ samples)
- Tabular data: Tree-based models often outperform neural nets
- Simpler models easier to interpret and debug
- Lower computational requirements

**Future Consideration**: Could add LSTM/GRU for large datasets with strong temporal patterns

### Why YAML for Configuration?

**Rationale**:
- Human-readable and editable
- Supports comments for documentation
- Widely supported (PyYAML library)
- No code execution (safer than Python config files)
- Easy to version control

### Why Command-Line Interface?

**Rationale**:
- Automation-friendly (CI/CD, cron jobs)
- No GUI dependencies
- Works on any platform (Linux servers, Docker, etc.)
- Easy to script and integrate
- Lower development complexity

**Future Enhancement**: Web interface or REST API

## Security Architecture

### Defense in Depth

The system implements multiple security layers:

1. **Input Validation Layer** (security.py)
   - Path traversal prevention
   - File extension validation
   - Path normalization

2. **Data Validation Layer** (helpers.py)
   - File existence checks
   - Column validation
   - Date range validation

3. **Output Sanitization Layer** (security.py)
   - CSV injection prevention
   - Value sanitization
   - Backup creation

### Security Design Principles

**Fail-Safe Defaults**:
- User confirmation required for overwrites
- Backups created before modifications
- Invalid inputs rejected early

**Least Privilege**:
- No unnecessary file system access
- Validates and restricts all paths
- No execution of user-provided data

**Defense Against Common Attacks**:
- Path Traversal: All paths validated and normalized
- CSV Injection: All output values sanitized
- File Overwrites: Backups and confirmations

## Scalability Considerations

### Current Limitations

**Data Size**: Designed for datasets up to 10,000 transactions
- All data loaded into memory (pandas DataFrame)
- Single-threaded processing
- Suitable for personal/small business use

**Processing Speed**: ~1-5 seconds for typical datasets
- Linear Regression: <1 second
- Decision Tree: 1-2 seconds
- Random Forest: 2-4 seconds (100 trees)
- Gradient Boosting: 2-5 seconds (100 iterations)

### Scaling Strategies (Future)

**For Larger Datasets** (100K+ transactions):
- Chunked data processing
- Incremental learning (partial_fit)
- Dask for distributed computing
- Database backend instead of CSV

**For Real-Time Predictions**:
- Model persistence (pickle/joblib)
- Pre-trained models
- API server (Flask/FastAPI)
- Caching layer

## Testing Architecture

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_helpers.py          # Unit tests (44 tests)
├── test_model_runner.py     # Integration tests (13 tests)
├── test_security.py         # Security tests
├── test_config.py           # Configuration tests
└── test_data/              # Sample data for testing
```

### Test Coverage Strategy

**Unit Tests** (helpers.py, security.py, config.py):
- Test individual functions in isolation
- Mock external dependencies
- Cover edge cases and error conditions

**Integration Tests** (model_runner.py):
- Test complete workflows
- Validate data flow through pipeline
- Test model training and prediction

**Security Tests**:
- Path validation scenarios
- CSV injection prevention
- Backup creation

**Current Coverage**: 43% (target: 80%)

## Future Architecture Enhancements

### Planned Improvements

1. **Model Persistence**
   - Save trained models to disk
   - Reload models for predictions
   - Versioning for models

2. **API Layer**
   - REST API for predictions
   - Web-based interface
   - Batch prediction endpoints

3. **Database Integration**
   - PostgreSQL/SQLite for data storage
   - Better data management
   - Historical prediction tracking

4. **Advanced Models**
   - LSTM for temporal patterns
   - Prophet for time series
   - AutoML for hyperparameter tuning

5. **Enhanced Features**
   - Category-based predictions
   - Multi-currency support
   - Anomaly detection

6. **Monitoring & Observability**
   - Prometheus metrics
   - Prediction accuracy tracking
   - Model drift detection

## References

- [scikit-learn Documentation](https://scikit-learn.org/stable/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Logging Framework](https://github.com/manoj-bhaskaran/My-Scripts)

## Support

For architecture questions or suggestions, please open an issue on the [GitHub repository](https://github.com/manoj-bhaskaran/expense-predictor/issues).
