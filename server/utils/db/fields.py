from sqlalchemy import Column, BigInteger


__all__ = [
    'IdField'
]


class IdField:
    def __new__(cls, *args, **kwargs):
        return Column(
            BigInteger,
            autoincrement=True,
            index=True,
            nullable=False,
            primary_key=True,
            unique=True,
        )
