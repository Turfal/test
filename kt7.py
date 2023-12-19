import pytest
import asyncio
import aiosqlite
import aiohttp


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


async def async_func():
    return 'result'


async def wrapper_func():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, async_func)
    return result


@pytest.mark.asyncio
async def test_async_func_thread(event_loop):
    result = await wrapper_func()
    assert result == 'result'


async def async_func_error():
    raise ValueError('test error')


async def wrapper_func_error():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, async_func_error)
    return result


@pytest.mark.asyncio
async def test_async_func_thread_error(event_loop):
    with pytest.raises(ValueError) as e:
        await wrapper_func_error()
    assert str(e.value) == 'test error'


async def async_func_http():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://jsonplaceholder.typicode.com/todos/1') as response:
            return await response.json()


@pytest.mark.asyncio
async def test_async_func_http(event_loop):
    data = await async_func_http()
    assert data['id'] == 1


async def async_func_db():
    async with aiosqlite.connect(':memory:') as db:
        async with db.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)') as cursor:
            await cursor.execute('INSERT INTO test (name) VALUES (?)', ('test',))
        async with db.execute('SELECT * FROM test') as cursor:
            data = await cursor.fetchall()
            return data


@pytest.mark.asyncio
async def test_async_func_db(event_loop):
    data = await async_func_db()
    assert data == [(1, 'test')]
