"""Tests for default profile censoring functionality."""

import pytest
import hashlib
from config.profiles.default_profile.profile_config import DefaultProfileProfile
from censor_utils.censoring import CensoringService


class TestDefaultProfileCensoring:
    """Test suite for default profile censoring functionality."""

    def test_sensitive_columns_configuration(self):
        """Test that default profile has correct sensitive columns configured."""
        profile = DefaultProfileProfile()
        sensitive_cols = profile.sensitive_columns
        
        assert 'CUSTOMER_ID' in sensitive_cols
        assert 'STORE_ADDRESS' in sensitive_cols
        assert sensitive_cols['CUSTOMER_ID'] == 'customer_id'
        assert sensitive_cols['STORE_ADDRESS'] == 'address'

    def test_censoring_mappings_configuration(self):
        """Test that default profile has correct censoring function mappings."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        assert 'customer_id' in mappings
        assert 'address' in mappings
        assert callable(mappings['customer_id'])
        assert callable(mappings['address'])

    def test_customer_id_censoring(self):
        """Test customer ID censoring using dealer code function."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test customer ID censoring
        customer_id = "CUST12345"
        censored = mappings['customer_id'](customer_id)
        
        # Should start with DEALER_ prefix and have 6-char hash
        assert censored.startswith("DEALER_")
        assert len(censored) == 13  # "DEALER_" + 6 chars
        assert censored != customer_id
        
        # Test consistency - same input should produce same output
        censored2 = mappings['customer_id'](customer_id)
        assert censored == censored2

    def test_customer_id_censoring_edge_cases(self):
        """Test customer ID censoring with edge cases."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test None input
        assert mappings['customer_id'](None) == ""
        
        # Test empty string
        assert mappings['customer_id']("") == ""
        
        # Test whitespace
        assert mappings['customer_id']("   ") == ""
        
        # Test numeric input
        numeric_id = 12345
        censored = mappings['customer_id'](numeric_id)
        assert censored.startswith("DEALER_")
        assert censored != str(numeric_id)

    def test_address_censoring_basic(self):
        """Test custom address censoring function."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test address censoring
        address = "123 Main St, New York, NY 10001"
        censored = mappings['address'](address)
        
        # Should start with ADDR_ prefix and have 8-char hash
        assert censored.startswith("ADDR_")
        assert len(censored) == 13  # "ADDR_" + 8 chars
        assert censored != address
        
        # Test consistency - same input should produce same output
        censored2 = mappings['address'](address)
        assert censored == censored2

    def test_address_censoring_edge_cases(self):
        """Test address censoring with edge cases."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test None input
        assert mappings['address'](None) == ""
        
        # Test empty string
        assert mappings['address']("") == ""
        
        # Test whitespace
        assert mappings['address']("   ") == ""
        
        # Test numeric input
        numeric_addr = 12345
        censored = mappings['address'](numeric_addr)
        assert censored.startswith("ADDR_")
        assert censored != str(numeric_addr)

    def test_address_censoring_various_formats(self):
        """Test address censoring with various address formats."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        addresses = [
            "123 Main St, New York, NY 10001",
            "456 Oak Ave, Los Angeles, CA 90210",
            "789 Pine Rd, Chicago, IL 60601",
            "321 Elm St, Houston, TX 77001"
        ]
        
        censored_addresses = []
        for addr in addresses:
            censored = mappings['address'](addr)
            assert censored.startswith("ADDR_")
            assert len(censored) == 13
            assert censored != addr
            censored_addresses.append(censored)
        
        # All censored addresses should be different
        assert len(set(censored_addresses)) == len(addresses)

    def test_censoring_service_integration(self):
        """Test integration with CensoringService."""
        profile = DefaultProfileProfile()
        censor_service = CensoringService()
        
        # Test that we can use the censoring service directly
        customer_id = "CUST98765"
        censored_customer = censor_service.censor_dealer_code(customer_id)
        assert censored_customer.startswith("DEALER_")
        
        # Test desensorizing
        desensorized = censor_service.desensorize_text(censored_customer)
        assert desensorized == customer_id

    def test_censoring_with_real_data(self):
        """Test censoring with real fridge sales data."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test with typical customer data
        test_data = {
            'CUSTOMER_ID': 'CUST001',
            'STORE_ADDRESS': '123 Broadway, New York, NY 10001'
        }
        
        censored_customer = mappings['customer_id'](test_data['CUSTOMER_ID'])
        censored_address = mappings['address'](test_data['STORE_ADDRESS'])
        
        assert censored_customer.startswith("DEALER_")
        assert censored_address.startswith("ADDR_")
        assert censored_customer != test_data['CUSTOMER_ID']
        assert censored_address != test_data['STORE_ADDRESS']

    def test_censoring_hash_consistency(self):
        """Test that censoring produces consistent hashes."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test customer ID hash consistency
        customer_id = "CUST12345"
        censored1 = mappings['customer_id'](customer_id)
        censored2 = mappings['customer_id'](customer_id)
        
        # Should produce same hash
        hash1 = censored1.split('_')[1]
        hash2 = censored2.split('_')[1]
        assert hash1 == hash2
        
        # Test address hash consistency
        address = "123 Main St"
        censored_addr1 = mappings['address'](address)
        censored_addr2 = mappings['address'](address)
        
        # Should produce same hash
        hash_addr1 = censored_addr1.split('_')[1]
        hash_addr2 = censored_addr2.split('_')[1]
        assert hash_addr1 == hash_addr2

    def test_censoring_different_inputs(self):
        """Test that different inputs produce different censored outputs."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test different customer IDs
        customer_ids = ["CUST001", "CUST002", "CUST003"]
        censored_ids = [mappings['customer_id'](cid) for cid in customer_ids]
        
        # All should be different
        assert len(set(censored_ids)) == len(customer_ids)
        
        # Test different addresses
        addresses = ["123 Main St", "456 Oak Ave", "789 Pine Rd"]
        censored_addresses = [mappings['address'](addr) for addr in addresses]
        
        # All should be different
        assert len(set(censored_addresses)) == len(addresses)


class TestDefaultProfileCensoringIntegration:
    """Integration tests for default profile censoring with query engine."""

    def test_censoring_with_query_engine(self):
        """Test censoring integration with query engine components."""
        from config.settings import Config
        
        # Create test configuration
        config = Config(
            google_api_key="test-key",
            generation_model="gemini-1.5-flash",
            port=9999,
            profile_name="default_profile"
        )
        
        profile = DefaultProfileProfile()
        
        # Test that censoring mappings work with profile
        mappings = profile.get_censoring_mappings()
        assert 'customer_id' in mappings
        assert 'address' in mappings
        
        # Test actual censoring
        test_customer = "CUST12345"
        test_address = "123 Main St, New York, NY 10001"
        
        censored_customer = mappings['customer_id'](test_customer)
        censored_address = mappings['address'](test_address)
        
        assert censored_customer != test_customer
        assert censored_address != test_address
        assert censored_customer.startswith("DEALER_")
        assert censored_address.startswith("ADDR_")

    def test_censoring_with_stats_generator(self):
        """Test censoring integration with response builder."""
        from query_syn.response.builder import ResponseBuilder
        
        profile = DefaultProfileProfile()
        response_builder = ResponseBuilder(profile)
        
        # Test that response builder can access censoring stats
        stats = response_builder.get_censor_stats()
        assert 'total_censored_fields' in stats
        assert 'dealer_mappings' in stats
        assert 'sample_mappings' in stats

    def test_censoring_consistency_across_operations(self):
        """Test that censoring is consistent across multiple operations."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test multiple censoring operations
        customer_id = "CUST99999"
        address = "999 Test Ave, Test City, TC 99999"
        
        # Censor multiple times
        results = []
        for _ in range(5):
            censored_customer = mappings['customer_id'](customer_id)
            censored_address = mappings['address'](address)
            results.append((censored_customer, censored_address))
        
        # All results should be identical
        first_customer, first_address = results[0]
        for censored_customer, censored_address in results[1:]:
            assert censored_customer == first_customer
            assert censored_address == first_address

    def test_censoring_with_empty_and_null_values(self):
        """Test censoring behavior with empty and null values."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test with truly empty/null values
        empty_values = [None, "", "   "]
        
        for value in empty_values:
            censored_customer = mappings['customer_id'](value)
            censored_address = mappings['address'](value)
            
            # Empty values should result in empty strings
            assert censored_customer == ""
            assert censored_address == ""
        
        # Test with falsy but non-empty values (these get censored)
        falsy_values = [0, False]
        
        for value in falsy_values:
            censored_customer = mappings['customer_id'](value)
            censored_address = mappings['address'](value)
            
            # Falsy values should be censored (not empty)
            assert censored_customer != ""
            assert censored_address != ""
            assert censored_customer.startswith("DEALER_")
            assert censored_address.startswith("ADDR_")

    def test_censoring_hash_algorithm_verification(self):
        """Test that the censoring uses the expected hash algorithm."""
        profile = DefaultProfileProfile()
        mappings = profile.get_censoring_mappings()
        
        # Test customer ID hash (should use MD5, first 6 chars)
        customer_id = "TEST123"
        censored = mappings['customer_id'](customer_id)
        hash_part = censored.split('_')[1]
        
        # Verify it's the expected MD5 hash
        expected_hash = hashlib.md5(customer_id.encode()).hexdigest()[:6].upper()
        assert hash_part == expected_hash
        
        # Test address hash (should use MD5, first 8 chars)
        address = "TEST ADDRESS"
        censored_addr = mappings['address'](address)
        hash_part_addr = censored_addr.split('_')[1]
        
        # Verify it's the expected MD5 hash
        expected_hash_addr = hashlib.md5(address.encode()).hexdigest()[:8].upper()
        assert hash_part_addr == expected_hash_addr
