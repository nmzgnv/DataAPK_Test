## Небольшой отчетик :)
* Не смог получить ответ на вопрос. Удаляются ли незатронутые ключи в запросе при параметре ```merge = 0``` поэтому
  эти ключи не удаляю
  
* Написал тесты на обработчики запросов
* Данные валидируются при помощи библиотеки ```pydantic``` и обертки ```aiohttp-pydantic```, в связи с чем возникла небольшая проблема:
---
* Попытался написать декоратор, который бы отлавливал выбрасываемые исключения (вместо лишних return), но библиотека ```aiohttp-pydantic``` вызывает
  исключения, связанные с приведением типов args, а явно указать параметры и их типы не представляется возможным
  https://stackoverflow.com/questions/37031928/type-annotations-for-args-and-kwargs
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
