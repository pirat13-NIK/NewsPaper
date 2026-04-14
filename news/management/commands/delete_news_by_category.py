from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from news.models import Category, Post, PostCategory
from django.utils import timezone


class Command(BaseCommand):
    """Удаляет все новости из указанной категории."""
    help = 'Удаляет все новости из указанной категории'

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки: category_name, --yes, --dry-run."""
        # Обязательный аргумент - название категории
        parser.add_argument(
            'category_name',
            type=str,
            help='Название категории, из которой нужно удалить новости'
        )

        # Опциональный аргумент для подтверждения
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Автоматически подтвердить удаление (без запроса)'
        )

        # Опциональный аргумент для сухого запуска (только показать что будет удалено)
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать только что будет удалено, без фактического удаления'
        )

    def handle(self, *args, **options):
        """Выполняет удаление новостей из категории с подтверждением."""
        category_name = options['category_name']
        auto_yes = options['yes']
        dry_run = options['dry_run']

        # Ищем категорию
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Ошибка: Категория "{category_name}" не найдена!')
            )
            return

        # Находим все новости в этой категории
        posts_in_category = Post.objects.filter(categories=category)
        posts_count = posts_in_category.count()

        if posts_count == 0:
            self.stdout.write(
                self.style.WARNING(f'Предупреждение: В категории "{category_name}" нет новостей для удаления.')
            )
            return

        # Показываем информацию о том, что будет удалено
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(f'Категория: {category.name}')
        self.stdout.write(f'Количество новостей к удалению: {posts_count}')
        self.stdout.write('=' * 60)

        if not dry_run:
            # Список новостей для удаления
            self.stdout.write('\nСписок новостей, которые будут удалены:')
            for post in posts_in_category[:10]:  # Показываем первые 10
                self.stdout.write(
                    f'   - "{post.title}" (ID: {post.id}, создано: {post.created_at.strftime("%d.%m.%Y")})')

            if posts_count > 10:
                self.stdout.write(f'   ... и еще {posts_count - 10} новостей')

        # Запрашиваем подтверждение
        if not auto_yes and not dry_run:
            self.stdout.write('\n' + '=' * 60)
            confirm = input(f'Вы действительно хотите удалить ВСЕ новости из категории "{category_name}"? (yes/no): ')

            if confirm.lower() != 'yes':
                self.stdout.write(self.style.SUCCESS('Операция отменена.'))
                return

        # Сухой запуск - только показываем что будет удалено
        if dry_run:
            self.stdout.write(self.style.WARNING('\nСУХОЙ ЗАПУСК: Ничего не удалено.'))
            self.stdout.write(f'Будет удалено {posts_count} новостей из категории "{category_name}"')
            return

        # Удаляем связи многие-ко-многим
        post_categories = PostCategory.objects.filter(category=category)
        post_categories_count = post_categories.count()
        post_categories.delete()

        # Удаляем сами посты
        deleted_count, _ = posts_in_category.delete()

        # Выводим результат
        self.stdout.write('=' * 60)
        self.stdout.write(
            self.style.SUCCESS(f'Успешно удалено {deleted_count} новостей из категории "{category_name}"')
        )
        self.stdout.write(f'Удалено связей: {post_categories_count}')
        self.stdout.write('=' * 60)

        # Дополнительная информация
        remaining_posts = Post.objects.filter(categories=category).count()
        if remaining_posts > 0:
            self.stdout.write(
                self.style.WARNING(f'Предупреждение: Осталось новостей в категории: {remaining_posts}')
            )