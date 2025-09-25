from typing import Dict, List, Any, Callable
import pandas as pd
from pathlib import Path
from config.profiles.base_profile import DataProfile


class DefaultProfileProfile(DataProfile):
    """Profile for fridge sales data with customer feedback and ratings."""
    
    def __init__(self, csv_file: str = None):
        self.profile_name = "default_profile"
        self.csv_file = csv_file or self.get_default_csv_file_path()
        self._inferred_columns = self._infer_columns()
    
    def get_csv_file_path(self) -> str:
        """Get the path to the CSV file for this profile."""
        return self.csv_file
    
    def get_default_csv_file_path(self) -> str:
        """Get the default CSV file path for this profile."""
        return str(Path(__file__).parent / "test_data/fridge_sales_with_rating.csv")
    
    def _infer_columns(self) -> Dict[str, List[str]]:
        """Infer column types from the CSV file."""
        try:
            df = pd.read_csv(self.csv_file, nrows=10)  # Read first 10 rows for inference
            columns = df.columns.tolist()
            
            text_cols = []
            date_cols = []
            numeric_cols = []
            
            for col in columns:
                if df[col].dtype == 'object':
                    # Try to parse as date
                    try:
                        pd.to_datetime(df[col].dropna().iloc[0] if not df[col].dropna().empty else '2024-01-01')
                        date_cols.append(col)
                    except:
                        text_cols.append(col)
                else:
                    numeric_cols.append(col)
            
            return {
                'required': columns,
                'text': text_cols,
                'date': date_cols,
                'numeric': numeric_cols
            }
        except Exception:
            # Fallback to known schema
            return {
                'required': ['ID', 'CUSTOMER_ID', 'FRIDGE_MODEL', 'BRAND', 'CAPACITY_LITERS', 'PRICE', 'SALES_DATE', 'STORE_NAME', 'STORE_ADDRESS', 'CUSTOMER_FEEDBACK', 'FEEDBACK_RATING'],
                'text': ['ID', 'CUSTOMER_ID', 'FRIDGE_MODEL', 'BRAND', 'STORE_NAME', 'STORE_ADDRESS', 'CUSTOMER_FEEDBACK', 'FEEDBACK_RATING'],
                'date': ['SALES_DATE'],
                'numeric': ['CAPACITY_LITERS', 'PRICE']
            }
    
    @property
    def required_columns(self) -> List[str]:
        return self._inferred_columns['required']
    
    @property
    def text_columns(self) -> List[str]:
        return self._inferred_columns['text']
    
    @property
    def date_columns(self) -> List[str]:
        return self._inferred_columns['date']
    
    @property
    def numeric_columns(self) -> List[str]:
        return self._inferred_columns['numeric']
    
    @property
    def sensitive_columns(self) -> Dict[str, str]:
        return {
            'CUSTOMER_ID': 'customer_id',
            'STORE_ADDRESS': 'address'
        }
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess fridge sales data."""
        # Fill NaN values in text columns
        for col in self.text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        
        # Convert date columns
        for col in self.date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert numeric columns
        for col in self.numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_censoring_mappings(self) -> Dict[str, Callable]:
        """Return censoring function mappings for sensitive columns."""
        from censor_utils.censoring import CensoringService
        censor_service = CensoringService()
        return {
            'customer_id': censor_service.censor_dealer_code,  # Reuse dealer code censoring
            'address': self._censor_address  # Custom address censoring
        }
    
    def _censor_address(self, address: Any) -> str:
        """Custom address censoring function for default profile."""
        if address is None:
            return ""
        address_str = str(address).strip()
        if address_str == "":
            return ""
        # Use a simple hash-based censoring for addresses
        import hashlib
        hashed = hashlib.md5(address_str.encode()).hexdigest()[:8].upper()
        return f"ADDR_{hashed}"
    
    def get_llm_provider(self) -> str:
        return "google"
    
    def get_llm_model(self) -> str:
        return "gemini-1.5-flash"
    
    def get_llm_system_prompt(self) -> str:
        return (
            "You are a strict JSON spec generator for pandas queries on fridge sales data. "
            "Output only a single JSON object with the allowed keys. No prose. No markdown."
        )
    
    def get_schema_hints(self, sample_data: str) -> str:
        return (
            f"Allowed columns: {', '.join(self.required_columns)}.\n" +
            "ALWAYS SELECT at least the BRAND, PRICE, and SALES_DATE when the user asks for sales analysis.\n" +
            "Allowed filter ops: eq, neq, gt, gte, lt, lte, in, contains, date_range.\n" +
            "If a date window is mentioned, include a date_range filter over SALES_DATE.\n" +
            "Use numeric comparisons for PRICE and CAPACITY_LITERS when applicable.\n" +
            "If grouping is natural (e.g., by BRAND), include group_by and aggregations.\n" +
            "The limit must be <= 500. Default to 100 if unspecified.\n" +
            "Context of the dataframe:\n" +
            sample_data +
            "Prompt hints for JSON spec creation:\n" +
            "- For questions about specific brands, add a filter with op 'eq' on BRAND.\n" +
            "- For questions about price ranges, use 'gte' or 'lte' filters on PRICE.\n" +
            "- For questions about capacity, filter or group by CAPACITY_LITERS.\n" +
            "- For questions about time periods, use a 'date_range' filter on SALES_DATE.\n" +
            "- For questions about ratings, filter by FEEDBACK_RATING (Positive, Negative, Neutral).\n" +
            "- For aggregations (e.g., average price, total sales), use 'aggregations' and 'group_by' as needed.\n" +
            "- For questions about stores, filter or group by STORE_NAME.\n" +
            "- Always return only the JSON object, no explanations or markdown.\n"
        )
    
    def get_example_queries(self) -> List[str]:
        return [
            "What is the average price of Samsung fridges?",
            "Show me the top 5 most expensive fridges sold in 2024",
            "How many fridges were sold by brand?",
            "Which stores had the most sales in January?",
            "What is the distribution of feedback ratings?",
            "Show me all fridges with capacity over 25 liters",
            "What are the average prices by brand and capacity?",
            "Which customers gave negative feedback and what did they buy?"
        ]
    
    def create_sources_from_df(self, df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
        """Create source dictionaries from DataFrame rows for fridge sales data."""
        sources: List[Dict[str, Any]] = []
        cols = set(df.columns)
        take = min(limit, len(df))
        
        for i in range(take):
            row = df.iloc[i]
            sources.append({
                'id': str(row['ID']) if 'ID' in cols else '',
                'customer_id': str(row['CUSTOMER_ID']) if 'CUSTOMER_ID' in cols else '',
                'fridge_model': str(row['FRIDGE_MODEL']) if 'FRIDGE_MODEL' in cols else '',
                'brand': str(row['BRAND']) if 'BRAND' in cols else '',
                'capacity': float(row['CAPACITY_LITERS']) if 'CAPACITY_LITERS' in cols and pd.notna(row['CAPACITY_LITERS']) else None,
                'price': float(row['PRICE']) if 'PRICE' in cols and pd.notna(row['PRICE']) else None,
                'sales_date': str(row['SALES_DATE']) if 'SALES_DATE' in cols else '',
                'store_name': str(row['STORE_NAME']) if 'STORE_NAME' in cols else '',
                'store_address': str(row['STORE_ADDRESS']) if 'STORE_ADDRESS' in cols else '',
                'feedback_rating': str(row['FEEDBACK_RATING']) if 'FEEDBACK_RATING' in cols else '',
                'feedback_preview': str(row['CUSTOMER_FEEDBACK'])[:100] + "..." if 'CUSTOMER_FEEDBACK' in cols and len(str(row['CUSTOMER_FEEDBACK'])) > 100 else str(row['CUSTOMER_FEEDBACK']) if 'CUSTOMER_FEEDBACK' in cols else ''
            })
        
        return sources
    
    def get_stats_columns(self) -> Dict[str, str]:
        return {
            'total_sales': 'ID',
            'average_price': 'PRICE',
            'brands_count': 'BRAND',
            'stores_count': 'STORE_NAME',
            'date_range': 'SALES_DATE',
            'capacity_range': 'CAPACITY_LITERS',
            'rating_distribution': 'FEEDBACK_RATING'
        }
    
    def get_language(self) -> str:
        return "en-US"
    
    def get_domain_terminology(self) -> Dict[str, str]:
        return {
            'fridge': 'refrigerator',
            'brand': 'manufacturer',
            'capacity': 'volume',
            'price': 'cost',
            'sales': 'purchases',
            'customer': 'buyer',
            'feedback': 'review',
            'rating': 'score',
            'store': 'retailer',
            'model': 'product'
        }