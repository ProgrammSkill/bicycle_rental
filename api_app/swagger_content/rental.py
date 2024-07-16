from drf_spectacular.utils import extend_schema, extend_schema_view


bicycles = extend_schema_view(
    get=extend_schema(
        summary="Список доступных велосипедов",
        tags=['Rental']
    ),
    post=extend_schema(
        summary="Создать велосипед",
        tags=['Rental']
    )
)


rent_bicycles = extend_schema_view(
    post=extend_schema(
        summary="Арендовать велосипед",
        tags=['Rental']
    )
)


return_bicycles = extend_schema_view(
    post=extend_schema(
        summary="Вернуть велосипед",
        tags=['Rental']
    )
)


rental_history = extend_schema_view(
    get=extend_schema(
        summary="История аренды велосипедов",
        tags=['Rental']
    )
)