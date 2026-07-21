"""
图书管理核心模块
负责图书信息的增删改查、借阅状态管理等核心业务逻辑
"""

from storage import JsonStorage
from exceptions import (
    BookNotFoundError,
    DuplicateBookError,
    InvalidInputError,
)


class BookManager:
    """图书管理器，提供所有图书操作接口"""

    # 借阅状态常量
    STATUS_AVAILABLE = "可借阅"
    STATUS_BORROWED = "已借出"

    def __init__(self, storage=None):
        """
        初始化图书管理器
        :param storage: 数据存储实例，不传则使用默认JSON存储
        """
        self.storage = storage or JsonStorage()

    def _validate_book_info(self, title, author, category="未分类"):
        """
        校验图书输入信息合法性
        :param title: 书名
        :param author: 作者
        :param category: 分类
        """
        if not title or not str(title).strip():
            raise InvalidInputError("书名", "不能为空")
        if not author or not str(author).strip():
            raise InvalidInputError("作者", "不能为空")
        if not category or not str(category).strip():
            raise InvalidInputError("分类", "不能为空")

    def add_book(self, title, author, category="未分类", publisher=""):
        """
        新增一本图书
        :param title: 书名
        :param author: 作者
        :param category: 图书分类
        :param publisher: 出版社（可选）
        :return: 新增的图书字典
        """
        self._validate_book_info(title, author, category)

        title = str(title).strip()
        author = str(author).strip()
        category = str(category).strip()
        publisher = str(publisher).strip()

        books = self.storage.load_all()

        # 检查重复：同书名+同作者视为重复
        for book in books:
            if book["title"] == title and book["author"] == author:
                raise DuplicateBookError(title, author)

        new_book = {
            "id": self.storage.get_next_id(),
            "title": title,
            "author": author,
            "category": category,
            "publisher": publisher,
            "status": self.STATUS_AVAILABLE,
        }
        books.append(new_book)
        self.storage.save_all(books)
        return new_book

    def delete_book(self, book_id):
        """
        根据ID删除图书
        :param book_id: 图书ID
        :return: 被删除的图书字典
        """
        if not book_id or not isinstance(book_id, int):
            raise InvalidInputError("图书ID", "必须为正整数")

        books = self.storage.load_all()
        for i, book in enumerate(books):
            if book["id"] == book_id:
                deleted = books.pop(i)
                self.storage.save_all(books)
                return deleted

        raise BookNotFoundError(book_id)

    def update_book(self, book_id, title=None, author=None,
                    category=None, publisher=None):
        """
        修改图书信息
        :param book_id: 图书ID
        :param title: 新书名（可选）
        :param author: 新作者（可选）
        :param category: 新分类（可选）
        :param publisher: 新出版社（可选）
        :return: 更新后的图书字典
        """
        if not book_id or not isinstance(book_id, int):
            raise InvalidInputError("图书ID", "必须为正整数")

        books = self.storage.load_all()
        for book in books:
            if book["id"] == book_id:
                if title is not None:
                    if not str(title).strip():
                        raise InvalidInputError("书名", "不能为空")
                    book["title"] = str(title).strip()
                if author is not None:
                    if not str(author).strip():
                        raise InvalidInputError("作者", "不能为空")
                    book["author"] = str(author).strip()
                if category is not None:
                    if not str(category).strip():
                        raise InvalidInputError("分类", "不能为空")
                    book["category"] = str(category).strip()
                if publisher is not None:
                    book["publisher"] = str(publisher).strip()

                self.storage.save_all(books)
                return book

        raise BookNotFoundError(book_id)

    def get_all_books(self):
        """
        获取全部图书列表
        :return: 图书列表
        """
        return self.storage.load_all()

    def get_book_by_id(self, book_id):
        """
        根据ID查询单本图书
        :param book_id: 图书ID
        :return: 图书字典
        """
        if not book_id or not isinstance(book_id, int):
            raise InvalidInputError("图书ID", "必须为正整数")

        books = self.storage.load_all()
        for book in books:
            if book["id"] == book_id:
                return book
        raise BookNotFoundError(book_id)

    def mark_borrowed(self, book_id):
        """
        标记图书为已借出
        :param book_id: 图书ID
        :return: 更新后的图书字典
        """
        return self._update_status(book_id, self.STATUS_BORROWED)

    def mark_returned(self, book_id):
        """
        标记图书为已归还（可借阅）
        :param book_id: 图书ID
        :return: 更新后的图书字典
        """
        return self._update_status(book_id, self.STATUS_AVAILABLE)

    def _update_status(self, book_id, new_status):
        """
        内部方法：更新图书借阅状态
        :param book_id: 图书ID
        :param new_status: 新状态
        :return: 更新后的图书字典
        """
        if not book_id or not isinstance(book_id, int):
            raise InvalidInputError("图书ID", "必须为正整数")

        books = self.storage.load_all()
        for book in books:
            if book["id"] == book_id:
                book["status"] = new_status
                self.storage.save_all(books)
                return book
        raise BookNotFoundError(book_id)
