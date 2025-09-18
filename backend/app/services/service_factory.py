"""
Service Factory for Vector Services
Provides automatic selection between optimized and standard vector services
"""
from typing import Optional
from app.services.vector_service import VectorService
from app.services.optimized_vector_service import OptimizedVectorService


class VectorServiceFactory:
    """
    Factory to create the best available vector service implementation
    Automatically selects optimized native multi-tenancy when available
    """

    _instance: Optional[object] = None
    _service_type: str = "unknown"

    @classmethod
    def get_vector_service(cls):
        """
        Get the best available vector service instance
        Returns optimized service with native multi-tenancy if supported,
        otherwise falls back to standard filtered service
        """
        if cls._instance is None:
            cls._instance = cls._create_best_service()

        return cls._instance

    @classmethod
    def _create_best_service(cls):
        """Create the best available vector service"""

        # Try optimized service first (native multi-tenancy)
        try:
            optimized_service = OptimizedVectorService()

            # Test if the service initialized properly
            if optimized_service.client and optimized_service.schema_initialized:
                cls._service_type = "optimized_native_mt"
                print("[VectorServiceFactory] Using OptimizedVectorService with native multi-tenancy")
                return optimized_service
            else:
                print("[VectorServiceFactory] OptimizedVectorService failed initialization")

        except Exception as e:
            print(f"[VectorServiceFactory] OptimizedVectorService creation failed: {str(e)}")

        # Fallback to standard service (filter-based isolation)
        try:
            standard_service = VectorService()
            if standard_service.client:
                cls._service_type = "standard_filtered"
                print("[VectorServiceFactory] Falling back to standard VectorService with filter-based isolation")
                return standard_service
            else:
                print("[VectorServiceFactory] Standard VectorService failed initialization")

        except Exception as e:
            print(f"[VectorServiceFactory] Standard VectorService creation failed: {str(e)}")

        # Last resort: return None (will trigger offline mode in agents)
        cls._service_type = "none"
        print("[VectorServiceFactory] No vector service available - agents will run without document context")
        return None

    @classmethod
    def get_service_info(cls) -> dict:
        """Get information about the active vector service"""
        return {
            "service_type": cls._service_type,
            "supports_native_multitenancy": cls._service_type == "optimized_native_mt",
            "performance_profile": {
                "optimized_native_mt": "3-5x faster, stronger isolation",
                "standard_filtered": "Standard performance, filter-based isolation",
                "none": "No vector search available"
            }.get(cls._service_type, "Unknown"),
            "security_level": {
                "optimized_native_mt": "Enterprise (shard-based isolation)",
                "standard_filtered": "Standard (filter-based isolation)",
                "none": "N/A"
            }.get(cls._service_type, "Unknown")
        }

    @classmethod
    def force_service_type(cls, service_type: str):
        """
        Force a specific service type for testing or configuration

        Args:
            service_type: "optimized", "standard", or "none"
        """
        cls._instance = None  # Reset instance

        if service_type == "optimized":
            cls._instance = OptimizedVectorService()
            cls._service_type = "optimized_native_mt"
        elif service_type == "standard":
            cls._instance = VectorService()
            cls._service_type = "standard_filtered"
        elif service_type == "none":
            cls._instance = None
            cls._service_type = "none"
        else:
            raise ValueError(f"Unknown service type: {service_type}")

        print(f"[VectorServiceFactory] Forced service type: {cls._service_type}")


# Convenience function for dependency injection
def get_vector_service():
    """Get the best available vector service - for use in dependency injection"""
    return VectorServiceFactory.get_vector_service()