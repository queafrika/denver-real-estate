
import frappe
from frappe.utils import flt


class CustomerQuery:

    def __init__(self):
        self.page_length = 20

        self.or_filters = []
        self.filters = []
        self.fields = [
            "name",
            "customer_name",
            "customer_group",
            "territory",
            "customer_type",
            "mobile_no",
            "email_id",
            "id_or_passport_no_or_reg_number"
        ]

    def query(self, page_length = 20, sort_order=None, search_term=None, start=0):

        result, count = [], 0

        self.page_length = page_length

        if search_term:
            self.build_search_filters(search_term)

        result, count = self.query_items(start=start)

        return {"result": result, "items_count": count}

    def build_search_filters(self, search_term):
        """Query search term in specified fields
        """
        # Default fields to search from
        search_fields = {"customer_name", "mobile_no", "email_id", "name"}

        # Build or filters for query
        search = "%{}%".format(search_term)
        for field in search_fields:
            self.or_filters.append([field, "like", search])

    def query_items(self, start=0):
        """Build a query to fetch Website Items based on field filters."""
        # MySQL does not support offset without limit,
        # frappe does not accept two parameters for limit
        # https://dev.mysql.com/doc/refman/8.0/en/select.html#id4651989
        count_items = frappe.db.get_list(
            "Customer",
            filters=self.filters,
            or_filters=self.or_filters,
            limit_page_length=184467440737095516,
            limit_start=0,  # get all items from this offset for total count ahead
        )
        count = len(count_items)

        items = frappe.db.get_list(
            "Customer",
            fields=self.fields,
            filters=self.filters,
            or_filters=self.or_filters,
            limit_page_length=self.page_length,
            limit_start=start,
        )

        for item in items:
            total_sales = flt(frappe.db.get_value("Sales Order", {"customer": item["name"]}, "sum(grand_total)"))
            total_payments = flt(frappe.db.get_value("Sales Order", {"customer": item["name"]}, "sum(advance_paid)"))
            balance = total_sales- total_payments

            item["total_sales"] = frappe.utils.fmt_money(total_sales, currency="Sh")
            item["total_payments"] = frappe.utils.fmt_money(total_payments, currency="Sh")
            item["balance"] = frappe.utils.fmt_money(balance, currency="Sh")
            
        return items, count


class OfferQuery:

    def __init__(self):
        self.page_length = 20

        self.or_filters = []
        self.filters = []
        self.fields = [
            "name",
            "customer",
            "plot",
            "sale_state",
            "currency",
            "sale_state",
            "project",
            "transaction_date",
            "branch",
            "sales_rep",
            "net_total",
            "status",
            "advance_paid"
        ]

    def query(self, page_length = 20, sort_order=None, search_term=None, start=0, customer=None):

        result, count = [], 0

        self.page_length = page_length;

        if search_term:
            self.build_search_filters(search_term)

        if customer is not None:
            self.filters.append(["customer", "=", customer])

        result, count = self.query_items(start=start)

        return {"result": result, "items_count": count}

    def build_search_filters(self, search_term):
        """Query search term in specified fields
        """
        # Default fields to search from
        search_fields = {"customer", "plot", "branch", "real_estate_project", "sales_rep"}

        # Build or filters for query
        search = "%{}%".format(search_term)
        for field in search_fields:
            self.or_filters.append([field, "like", search])

    def query_items(self, start=0):
        """Build a query to fetch Website Items based on field filters."""
        # MySQL does not support offset without limit,
        # frappe does not accept two parameters for limit
        # https://dev.mysql.com/doc/refman/8.0/en/select.html#id4651989
        count_items = frappe.db.get_list(
            "Sales Order",
            filters=self.filters,
            or_filters=self.or_filters,
            limit_page_length=184467440737095516,
            limit_start=start,  # get all items from this offset for total count ahead
            
        )
        count = len(count_items)

        items = frappe.db.get_list(
            "Sales Order",
            fields=self.fields,
            filters=self.filters,
            or_filters=self.or_filters,
            limit_page_length=self.page_length,
            limit_start=start,
        )
        return items, count


class SalesQuery:

    def __init__(self):
        self.page_length = 20

        self.or_filters = []
        self.filters = []
        self.fields = [
            "name",
            "customer",
            "plot",
            "posting_date",
            "branch",
            "sales_rep",
            "project",
            "net_total",
            "status",
            "total_advance",
            "outstanding_amount",
            "due_date",
        ]

    def query(self, page_length = 20, sort_order=None, search_term=None, start=0, customer=None):

        result, count = [], 0

        self.page_length = page_length;

        if search_term:
            self.build_search_filters(search_term)

        if customer is not None:
            self.filters.append(["customer", "=", customer])

        result, count = self.query_items(start=start)

        return {"result": result, "items_count": count}

    def build_search_filters(self, search_term):
        """Query search term in specified fields
        """
        # Default fields to search from
        search_fields = {"customer", "plot", "branch", "real_estate_project", "sales_rep"}

        # Build or filters for query
        search = "%{}%".format(search_term)
        for field in search_fields:
            self.or_filters.append([field, "like", search])

    def query_items(self, start=0):
        """Build a query to fetch Website Items based on field filters."""
        # MySQL does not support offset without limit,
        # frappe does not accept two parameters for limit
        # https://dev.mysql.com/doc/refman/8.0/en/select.html#id4651989
        count_items = frappe.db.get_list(
            "Sales Invoice",
            filters=self.filters,
            or_filters=self.or_filters,
            limit_page_length=184467440737095516,
            limit_start=start,  # get all items from this offset for total count ahead
            
        )
        count = len(count_items)

        items = frappe.db.get_list(
            "Sales Invoice",
            fields=self.fields,
            filters=self.filters,
            or_filters=self.or_filters,
            limit_page_length=self.page_length,
            limit_start=start,
        )
        return items, count



class PaymentsQuery:

    def __init__(self):
        self.page_length = 20

        self.or_filters = []
        self.filters = []
        self.fields = [
            "name",
            "party_name",
            "posting_date",
            "status",
            "mode_of_payment",
            "paid_amount",
            "reference_no"
        ]

    def query(self, page_length = 20, sort_order=None, search_term=None, start=0, sale_name=None, offer_name=None,):

        result, count = [], 0

        self.page_length = page_length;

        if search_term:
            self.build_search_filters(search_term)

        if sale_name:
            self.filters.append(["Payment Entry Reference", "reference_name", "=", sale_name])

        if offer_name:
            self.filters.append(["Payment Entry Reference", "reference_name", "=", offer_name])

        result, count = self.query_items(start=start)


        return {"result": result, "items_count": count}

    def build_search_filters(self, search_term):
        """Query search term in specified fields
        """
        # Default fields to search from
        search_fields = {"customer", "reference_no", "mode_of_payment",}

        # Build or filters for query
        search = "%{}%".format(search_term)
        for field in search_fields:
            self.or_filters.append([field, "like", search])

    def query_items(self, start=0):
        """Build a query to fetch Website Items based on field filters."""
        # MySQL does not support offset without limit,
        # frappe does not accept two parameters for limit
        # https://dev.mysql.com/doc/refman/8.0/en/select.html#id4651989
        count_items = frappe.db.get_list(
            "Payment Entry",
            filters=self.filters,
            or_filters=self.or_filters,
            limit_page_length=184467440737095516,
            limit_start=start,  # get all items from this offset for total count ahead
            
        )
        count = len(count_items)

        items = frappe.db.get_all(
            "Payment Entry",
            fields=self.fields,
            filters=self.filters,
            or_filters=self.or_filters,
            limit_page_length=self.page_length,
            limit_start=start,
        )
        return items, count

