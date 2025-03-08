import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview, TableCellRightClickMenu, TableHeaderRightClickMenu


class TableviewScrollable(Tableview):
    def __init__(
        self,
        master=None,
        bootstyle=DEFAULT,
        coldata=[],
        rowdata=[],
        paginated=False,
        searchable=False,
        yscrollbar=True,
        autofit=False,
        autoalign=True,
        stripecolor=None,
        pagesize=10,
        height=10,
        delimiter=",",
    ):
        """
        Parameters:

            master (Widget):
                The parent widget.

            bootstyle (str):
                A style keyword used to set the focus color of the entry
                and the background color of the date button. Available
                options include -> primary, secondary, success, info,
                warning, danger, dark, light.

            coldata (List[str | Dict]):
                An iterable containing either the heading name or a
                dictionary of column settings. Configurable settings
                include >> text, image, command, anchor, width, minwidth,
                maxwidth, stretch. Also see `Tableview.insert_column`.

            rowdata (List):
                An iterable of row data. The lenth of each row of data
                must match the number of columns. Also see
                `Tableview.insert_row`.

            paginated (bool):
                Specifies that the data is to be paginated. A pagination
                frame will be created below the table with controls that
                enable the user to page forward and backwards in the
                data set.

            pagesize (int):
                When `paginated=True`, this specifies the number of rows
                to show per page.

            searchable (bool):
                If `True`, a searchbar will be created above the table.
                Press the <Return> key to initiate a search. Searching
                with an empty string will reset the search criteria, or
                pressing the reset button to the right of the search
                bar. Currently, the search method looks for any row
                that contains the search text. The filtered results
                are displayed in the table view.

            yscrollbar (bool):
                If `True`, a vertical scrollbar will be created to the right
                of the table.

            autofit (bool):
                If `True`, the table columns will be automatically sized
                when loaded based on the records in the current view.
                Also see `Tableview.autofit_columns`.

            autoalign (bool):
                If `True`, the column headers and data are automatically
                aligned. Numbers and number headers are right-aligned
                and all other data types are left-aligned. The auto
                align method evaluates the first record in each column
                to determine the data type for alignment. Also see
                `Tableview.autoalign_columns`.

            stripecolor (Tuple[str, str]):
                If provided, even numbered rows will be color using the
                (background, foreground) specified. You may specify one
                or the other by passing in **None**. For example,
                `stripecolor=('green', None)` will set the stripe
                background as green, but the foreground will remain as
                default. You may use standand color names, hexadecimal
                color codes, or bootstyle color keywords. For example,
                ('light', '#222') will set the background to the "light"
                themed ttkbootstrap color and the foreground to the
                specified hexadecimal color. Also see
                `Tableview.apply_table_stripes`.

            height (int):
                Specifies how many rows will appear in the table's viewport.
                If the number of records extends beyond the table height,
                the user may use the mousewheel or scrollbar to navigate
                the data.

            delimiter (str):
                The character to use as a delimiter when exporting data
                to CSV.
        """
        self.yscrollbar = yscrollbar
        super().__init__(
            master,
            bootstyle,
            coldata,
            rowdata,
            paginated,
            searchable,
            autofit,
            autoalign,
            stripecolor,
            pagesize,
            height,
            delimiter,
        )

    def _build_tableview_widget(self, coldata, rowdata, bootstyle):
        """Build the data table"""
        if self._searchable:
            self._build_search_frame()

        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=YES, side=TOP)

        self.view = ttk.Treeview(
            master=table_frame,
            columns=[x for x in range(len(coldata))],
            height=self._height,
            selectmode=EXTENDED,
            show=HEADINGS,
            bootstyle=f"{bootstyle}-table",
        )
        self.view.pack(fill=BOTH, expand=YES, side=LEFT)

        if self.yscrollbar:
            self.ybar = ttk.Scrollbar(
                master=table_frame, command=self.view.yview, orient=VERTICAL
            )
            self.ybar.pack(fill=Y, side=RIGHT)
            self.view.configure(yscrollcommand=self.ybar.set)

        self.hbar = ttk.Scrollbar(
            master=self, command=self.view.xview, orient=HORIZONTAL
        )
        self.hbar.pack(fill=X)
        self.view.configure(xscrollcommand=self.hbar.set)

        if self._paginated:
            self._build_pagination_frame()

        self.build_table_data(coldata, rowdata)

        self._rightclickmenu_cell = TableCellRightClickMenu(self)
        self._rightclickmenu_head = TableHeaderRightClickMenu(self)
        self._set_widget_binding()