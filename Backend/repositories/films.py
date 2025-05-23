from typing import Optional, List

from sqlalchemy import select

from app.db.models import FilmOrm
from app.db.setup import new_session


class FilmRepository:
    @staticmethod
    async def get_first_n_films(
            n: int = 10,
            skip: int = 0,
            search_query: Optional[str] = None  # <--- ДОБАВЛЕН ПАРАМЕТР
    ) -> List[FilmOrm]:
        """
        Получает первые N фильмов из БД с возможностью пропустить первые skip записей
        и опциональным поиском по названию.

        :param n: Количество записей для получения
        :param skip: Количество записей для пропуска
        :param search_query: Строка для поиска по названию фильма (опционально)
        :return: Список фильмов
        """
        async with new_session() as session:
            stmt = select(FilmOrm)  #

            if search_query:
                # Добавляем фильтрацию по названию фильма (title)
                # FilmOrm.title - это поле в вашей модели SQLAlchemy
                # ilike для регистронезависимого поиска
                stmt = stmt.filter(FilmOrm.title.ilike(f"%{search_query}%"))

            stmt = stmt.order_by(FilmOrm.id).offset(skip).limit(n)  #
            result = await session.execute(stmt)  #
            return result.scalars().all()  #

    @staticmethod
    async def get_film_by_id(
            film_id: int
    ) -> Optional[FilmOrm]:
        """
        Получает один фильм из БД по его идентификатору

        :param film_id: Идентификатор фильма
        :return: Объект фильма или None, если не найден
        """
        async with new_session() as session:
            result = await session.execute(
                select(FilmOrm).where(FilmOrm.movie_id == film_id)
            )
            return result.scalars().first()

    @staticmethod
    async def increment_vote_count_by_id(
            film_id: int
    ) -> Optional[FilmOrm]:
        """
        Увеличивает счетчик голосов (vote_count) на 1 для указанного фильма

        :param film_id: Идентификатор фильма
        :return: Обновленный объект фильма или None, если не найден
        """
        async with new_session() as session:
            # Получаем фильм
            result = await session.execute(
                select(FilmOrm).where(FilmOrm.movie_id == film_id)
            )
            film = result.scalars().first()

            if film is not None:
                # Увеличиваем vote_count на 1
                film.vote_count += 1
                await session.commit()
                await session.refresh(film)

            return film
