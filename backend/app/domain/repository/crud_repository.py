"""Generic protocol defining basic repository operations."""

from typing import Generic, Protocol, TypeVar

T = TypeVar("T")
ID_contra = TypeVar("ID_contra", contravariant=True)


class CrudRepository(Protocol, Generic[T, ID_contra]):
    """Specify CRUD operations supported by repositories for an entity type."""

    def get_by_id(self, entity_id: ID_contra) -> T | None:
        """Return the entity with the given ID, or None when it is absent."""
        ...

    def list_all(self) -> list[T]:
        """Return all entities available in the repository."""
        ...

    def add(self, entity: T) -> T:
        """Persist or store an entity and return it."""
        ...

    def delete(self, entity_id: ID_contra) -> bool:
        """Delete the entity with the given ID and report whether it existed."""
        ...
