import frappe, time, uuid
from unittest import mock, TestCase
from shopee_open_api.utils.client import get_shopless_client
from shopee_open_api.utils.datetime import datetime_string_from_unix
from shopee_open_api.python_shopee.pyshopee2.client import Client
from .mock_data.products import product_base_info, model_list
from shopee_open_api.shopee_models.product import Product


class ShopeeProductTest(TestCase):
    @classmethod
    def setUpClass(cls):

        cls.SHOP_ID = uuid.uuid4().hex.upper()[0:6]

        cls.client = get_shopless_client()

        token = frappe.get_doc(
            doctype="Shopee Token",
            shop_id=cls.SHOP_ID,
            access_token="ACCESS TOKEN",
            refresh_token="REFRESH TOKEN",
            token_expiration_unix=int(time.time()),
            authorization_time=datetime_string_from_unix(time.time()),
            expiration_time=datetime_string_from_unix(time.time() + 60000),
        )
        token.insert()
        cls.token = token

        shop = frappe.get_doc(
            doctype="Shopee Shop",
            name=cls.SHOP_ID,
            shop_id=cls.SHOP_ID,
            shop_name="TEST SHOP",
            token=cls.SHOP_ID,
        )
        shop.insert()
        cls.shop = shop

        for product in product_base_info:
            """Set new product id for each item so that they don't clash with real products in the database"""
            product["item_id"] = uuid.uuid4().hex.upper()[0:16]

        cls.products = [
            Product(product, shop_id=cls.SHOP_ID) for product in product_base_info
        ]

        cls.single_products = [
            product for product in cls.products if not product.has_model
        ]

        cls.variant_products = [
            product for product in cls.products if product.has_model
        ]

    @classmethod
    def tearDownClass(cls):

        product_ids = frappe.db.get_list(
            "Shopee Product",
            filters={
                "shopee_shop": cls.SHOP_ID,
            },
            pluck="name",
        )
        for product_id in product_ids:
            frappe.get_doc("Shopee Product", product_id).delete()

        cls.shop.delete()
        cls.token.delete()

    def tearDown(self):
        product_ids = frappe.db.get_list(
            "Shopee Product",
            filters={
                "shopee_shop": self.SHOP_ID,
            },
            pluck="name",
        )
        for product_id in product_ids:
            frappe.get_doc("Shopee Product", product_id).delete()

    def test_single_product_is_existing_in_database(self):
        product = self.single_products[0]
        self.assertFalse(product.is_existing_in_database)

        product.update_or_insert()
        self.assertTrue(product.is_existing_in_database)

    def test_product_with_model_is_existing_in_database(self):
        product = self.variant_products[0]
        product.model_details = model_list
        product.models = product.model_details["model"]
        product.instantiate_models()

        self.assertFalse(product.is_existing_in_database)

        product.update_or_insert()
        self.assertTrue(product.is_existing_in_database)

        """If the number of variants on shopee and database aren't the same, return False"""
        model = frappe.get_doc("Shopee Product", product.models[0].make_primary_key())
        model.delete()
        self.assertFalse(product.is_existing_in_database)

    def test_product_to_json(self):
        single_product = self.single_products[0]
        self.assertIsInstance(single_product.to_json(), dict)

        product_with_model = self.variant_products[0]
        self.assertIsInstance(product_with_model.to_json(), dict)

    def test_update_or_insert_single_product(self):

        product = self.single_products[0]
        self.assertEqual(
            frappe.db.count("Shopee Product", {"name": product.make_primary_key()}),
            0,
        )

        product.update_or_insert()
        self.assertEqual(
            frappe.db.count("Shopee Product", {"name": product.make_primary_key()}),
            1,
        )

        product.update_or_insert()
        self.assertEqual(
            frappe.db.count("Shopee Product", {"name": product.make_primary_key()}),
            1,
        )

    def test_update_or_insert_product_with_model(self):

        product = self.variant_products[0]
        product.model_details = model_list
        product.models = product.model_details["model"]
        product.instantiate_models()

        self.assertEqual(
            frappe.db.count(
                "Shopee Product", {"shopee_product_id": product.get_product_id()}
            ),
            0,
        )

        product.update_or_insert()
        self.assertEqual(
            frappe.db.count(
                "Shopee Product", {"shopee_product_id": product.get_product_id()}
            ),
            len(product.models),
        )

        product.update_or_insert()
        self.assertEqual(
            frappe.db.count(
                "Shopee Product", {"shopee_product_id": product.get_product_id()}
            ),
            len(product.models),
        )
