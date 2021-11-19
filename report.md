* Попытался написать декоратор, который бы отлавливал выбрасываемые исключения, но библиотека aiohttp-pydantic бросала
  исключения, связанные с приведением типов
    ```
    raise HandleAPIException('FROM currency not found')
    
  ...
    
  def handle_error(func: Callable[..., R]) -> Callable[..., R]:
        def wrapper(*args: Any):
            try:
                return func(*args)
            except HandleAPIException as error:
                return web.json_response({'error': error}, status=400)
    return wrapper
    ```

  вместо
    ```
    return web.json_response({
        'error': 'FROM currency not found'
    }, status=400)
    ```
