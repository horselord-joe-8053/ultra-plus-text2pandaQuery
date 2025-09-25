"""Consolidated response building with formatting and statistics generation."""

import pandas as pd
from typing import Dict, Any, Optional, List
from config.profiles import DataProfile
from config.logging_config import get_rag_logger
from censor_utils.censoring import CensoringService

logger = get_rag_logger()


class ResponseBuilder:
    """
    Consolidated response building with formatting and statistics generation.
    Combines response building, formatting, and statistics functionality.
    """
    
    def __init__(self, profile: DataProfile):
        self.profile = profile
        self.censor = CensoringService()
    
    def build_response(self, 
                      df_result: Optional[pd.DataFrame], 
                      query_spec: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a complete response from query results."""
        
        if df_result is None or df_result.empty:
            return self._build_empty_response(query_spec)
        
        # Format for display and return
        table = self._format_dataframe_for_display(df_result)
        sources = self.profile.create_sources_from_df(df_result)
        
        return {
            'answer': table, 
            'sources': sources, 
            'confidence': 'high', 
            'query_spec': query_spec
        }
    
    def _build_empty_response(self, query_spec: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build response when no results are found."""
        return {
            'answer': 'No matching rows for your request.', 
            'sources': [], 
            'confidence': 'low', 
            'query_spec': query_spec
        }
    
    def _format_dataframe_for_display(self, 
                                    df: pd.DataFrame, 
                                    max_rows: int = 50, 
                                    max_chars: int = 6000) -> str:
        """Format a DataFrame into a compact CSV-like table string for display."""
        try:
            if len(df) > max_rows:
                df = df.head(max_rows)
            
            table = df.to_csv(index=False)
            
            # If still too large, reduce rows further
            while len(table) > max_chars and len(df) > 5:
                df = df.head(max(5, len(df) // 2))
                table = df.to_csv(index=False)
            
            logger.debug("Formatted DataFrame for display")
            return table
            
        except Exception as e:
            logger.warning(f"Failed to format DataFrame for display: {e}")
            return ""
    
    def format_dataframe_for_prompt(self, 
                                  df: pd.DataFrame, 
                                  max_rows: int = 50, 
                                  max_chars: int = 6000) -> str:
        """Format a DataFrame into a compact CSV-like table string for prompting."""
        try:
            if len(df) > max_rows:
                df = df.head(max_rows)
            table = df.to_csv(index=False)
            # If still too large, reduce rows further
            while len(table) > max_chars and len(df) > 5:
                df = df.head(max(5, len(df) // 2))
                table = df.to_csv(index=False)
            return table
        except Exception as e:
            logger.warning(f"Failed to format DataFrame for prompt: {e}")
            return ""
    
    # Statistics generation methods (from StatsGenerator)
    def generate_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive statistics for the dataset."""
        stats_columns = self.profile.get_stats_columns()
        
        stats = {'total_records': len(df)}
        
        # Generate stats based on profile configuration
        for stat_name, column in stats_columns.items():
            if column in df.columns:
                if stat_name == 'dealers_count':
                    stats[stat_name] = df[column].nunique()
                elif stat_name == 'average_score':
                    stats[stat_name] = float(df[column].mean())
                elif stat_name == 'repair_types':
                    stats[stat_name] = df[column].value_counts().head(10).to_dict()
                elif stat_name == 'date_range':
                    stats[stat_name] = {
                        'earliest': str(df[column].min()),
                        'latest': str(df[column].max())
                    }
        
        # Add censoring statistics
        stats['censor_stats'] = self.get_censor_stats()
        return stats
    
    def get_censor_stats(self) -> Dict[str, Any]:
        """Get statistics about data censoring operations."""
        return self.censor.get_stats()
    
    def get_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic dataset statistics."""
        return {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'null_counts': df.isnull().sum().to_dict()
        }
    
    def get_column_stats(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific column."""
        if column not in df.columns:
            return {'error': f'Column {column} not found'}
        
        col_data = df[column]
        stats = {
            'column_name': column,
            'dtype': str(col_data.dtype),
            'null_count': col_data.isnull().sum(),
            'unique_count': col_data.nunique()
        }
        
        # Add type-specific statistics
        if pd.api.types.is_numeric_dtype(col_data):
            stats.update({
                'mean': float(col_data.mean()) if not col_data.empty else None,
                'median': float(col_data.median()) if not col_data.empty else None,
                'std': float(col_data.std()) if not col_data.empty else None,
                'min': float(col_data.min()) if not col_data.empty else None,
                'max': float(col_data.max()) if not col_data.empty else None
            })
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            stats.update({
                'earliest': str(col_data.min()) if not col_data.empty else None,
                'latest': str(col_data.max()) if not col_data.empty else None
            })
        else:
            # For categorical/text columns
            value_counts = col_data.value_counts().head(10)
            stats['top_values'] = value_counts.to_dict()
        
        return stats


# Standalone functions for backward compatibility
def format_dataframe_for_prompt(df: pd.DataFrame, max_rows: int = 50, max_chars: int = 6000) -> str:
    """Standalone function for formatting DataFrame for prompts (backward compatibility)."""
    try:
        if len(df) > max_rows:
            df = df.head(max_rows)
        table = df.to_csv(index=False)
        while len(table) > max_chars and len(df) > 5:
            df = df.head(max(5, len(df) // 2))
            table = df.to_csv(index=False)
        return table
    except Exception as e:
        logger.warning(f"Failed to format DataFrame for prompt: {e}")
        return ""


def create_sources_from_df(df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
    """
    DEPRECATED: This function has been moved to profile-specific implementations.
    Use profile.create_sources_from_df() instead for profile-specific source creation.
    """
    logger.warning("create_sources_from_df() standalone function is deprecated. Use profile.create_sources_from_df() instead.")
    
    # Fallback generic implementation
    sources: List[Dict[str, Any]] = []
    cols = set(df.columns)
    take = min(limit, len(df))
    
    for i in range(take):
        row = df.iloc[i]
        source = {}
        for col in cols:
            # Generic source creation - just include all columns
            if pd.notna(row[col]):
                source[col.lower()] = str(row[col])
            else:
                source[col.lower()] = ''
        sources.append(source)
    
    return sources


# Backward compatibility alias
StatsGenerator = ResponseBuilder