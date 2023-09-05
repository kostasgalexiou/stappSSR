import streamlit as st
from ssr_conversion import generate_output
import streamlit.components.v1 as stc
from sqlite3_fxns import *
from fnxns import detect_duplicate_markers

conn = sqlite3.connect("species.db", check_same_thread=False)
c = conn.cursor()

HTML_BANNER = """
    <div style="background-color:#464e5f;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">SSR Conversion</h1>
    </div>
    """


def main():
    """SSR Conversion"""
    # st.title("MetaData Extraction App")
    stc.html(HTML_BANNER)

    # species = [x for x in select_all_tables()[0]]
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables_sql = c.fetchall()
    species_list = [x[0] for x in tables_sql]

    menu = [
        "About",
        "Species info",
        "Add species and/or markers",
        "Format conversion",
        "Help",
    ]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "About":
        st.markdown(
            '<h align="center"><font size="5"><mark style="background-color: lightgrey">*SSR '
            "Conversion*</mark> is a streamlit application for converting SRR genotyping "
            "data into a binary format for presence/absence of the marker allele.</font></h>",
            unsafe_allow_html=True,
        )

    elif choice == "Help":
        st.markdown(
            '<font size="4">\n\n- Input data is a '
            "<b>comma-separated (CSV)</b> file where rows represent samples and columns respresent the SSR "
            "markers. Below you can see an example of input data:</font>\n\n\n",
            unsafe_allow_html=True,
        )
        st.code(
            "Line,cesi98,cesi976,cesi17,...\n"
            "1124/20,185,273,193,...\n"
            "1125/20,185/191,273,193,...\n"
            "1131/20,-,273,-,...\n\n"
        )
        st.markdown(
            '<font size="4">\n\n- Species info Track</font>\n\n', unsafe_allow_html=True
        )
        st.markdown(
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;In this track you can see a table with all the "
            "marker alleles, grouped by species",
            unsafe_allow_html=True
        )
        st.markdown(
            '<font size="4">\n\n- Add new species and/or markers</font>\n\n',
            unsafe_allow_html=True,
        )
        st.markdown(
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rerererere",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p align="left"><font size="4">Points to consider:\n\n'
            '+ Species available in the database can be seen from "Species Info" at the Sidebar Menu\n'
            "+ fdsfs</font></p>",
            unsafe_allow_html=True,
        )

    elif choice == "Species info":
        if len(species_list) != 0:
            lista = list()
            listb = list()
            for i in species_list:
                entries = c.execute("""SELECT * FROM %s""" % i).fetchall()
                for e in entries:
                    f = list(e)
                    f.append(i)
                    lista.append(f)
                listb = sorted(lista, key=lambda x:x[0].lower())

            transp_listb = zip(*listb)
            df = pd.DataFrame.from_records(transp_listb).T
            df.columns = ["marker_name", "user", "date introduced", "species"]
            st.write(
                "Species available in the database, with their corresponding SSR markers:"
            )
            st.dataframe(df, hide_index=True)
        else:
            st.warning(
                'No species table available. Please run "Add species and/or markers" from sidebar menu to a new '
                "species and/or markers for a species."
            )
            exit(0)

    elif choice == "Add species and/or markers":
        st.subheader("Add new species and markers?")
        st.code("Available species in the database: %s" % species_list)

        option = st.radio(
            "Do you want to add a new species?", options=["yes", "no"], horizontal=True
        )

        if option == "yes":
            user = st.text_input("Introduce your full name")
            new_species = st.text_input(
                "Introduce the name of the species (Latin name or common name)"
            )
            alleles_file = st.file_uploader("Upload marker file", type=["txt", "csv"])

            if alleles_file is not None and new_species is not None:
                alleles_df = pd.read_csv(alleles_file, header=None)
                create_and_populate_table(new_species, alleles_df, user)
                st.success(
                    "%s markers were added to the database correctly"
                    % new_species.upper()
                )
        else:
            st.markdown(
                "##### It looks like that you want to add a new set of markers. Please fill in the information below: #####"
            )
            user = st.text_input("Introduce your full name")
            selected_species = st.selectbox("Select species from list:", species_list)
            new_marker = st.text_area("Provide new marker(s); one per line")
            marker_addition = st.button("Add markers")

            if marker_addition:
                (
                    common_markers,
                    new_marker_list,
                    new_marker_list2,
                ) = detect_duplicate_markers(new_marker, selected_species)

                if len(common_markers) != 0:
                    st.write(
                        "Marker(s) %s already present in the %s database. Ignoring..."
                        % (common_markers, selected_species)
                    )
                    for x in common_markers:
                        new_marker_list.remove(x)
                        new_marker_list2 = [[x] for x in new_marker_list]
                    add_markers(selected_species, new_marker_list2, user)
                else:
                    add_markers(selected_species, new_marker_list2, user)
                st.success(
                    "Marker(s) %s were added successfully to the %s database"
                    % (new_marker_list, selected_species.upper())
                )

                new_data = view_all_data(selected_species)
                new_data2 = sorted([x[0] for x in new_data], key=lambda x:x[0].lower())
                df = pd.DataFrame(new_data2, columns=["%s markers" % selected_species])
                st.markdown(
                    "###### Below you the have the updated list of markers in the %s database ######"
                    % selected_species.upper()
                )
                st.table(df)

    elif choice == "Format conversion":
        st.subheader("Conversion from alleles to binary format")
        selected_species = st.selectbox("Select species of interest", species_list)

        if not selected_species:
            st.error("Remember to add a species to the database before proceeding!!!!")

        # # ensure that species table has at least one marker present
        # if (
        #     c.execute("""SELECT COUNT(*) FROM %s""" % selected_species).fetchone()[0]
        #     == 0
        # ):
        #     st.warning(
        #         'Your {0} table does not contain any markers. Please run "Add species" from sidebar '
        #         "menu to add markers for {0}.".format(selected_species)
        #     )
        #     exit(0)
        else:
            in_data = st.file_uploader("Upload you data", type=["csv"])
            st.warning(
                "Please make sure that non-utf8 characters are not present in line names "
                "(e.g. í, ó, é, á, ñ, etc.)"
            )

            if in_data is not None:
                species_alleles = view_all_data(selected_species)
                dataf = pd.read_csv(in_data)
                rows, columns = list(dataf.shape)
                st.info(
                    "##### You have uploaded a {0} file named '{1}' with {2} rows and {3} columns.\n"
                    "Before you proceed, make sure that your file has column headers!".format(
                        in_data.type.split("/")[1].upper(),
                        in_data.name.upper(),
                        rows,
                        columns,
                    )
                )
                with st.expander("##### Check you Input Data #####"):
                    st.dataframe(dataf)

                convert = st.button("##### Run data conversion #####")

                if convert:
                    species_alleles2 = [x[0] for x in species_alleles]
                    results_df = generate_output(dataf, species_alleles2)
                    st.success("Data conversion completed successfully!")

                    with st.expander("##### Converted Data #####"):
                        st.dataframe(results_df)

                    FileDownloader(
                        results_df.to_csv(index=False),
                        filename=in_data.name.split(".")[0],
                    ).download()


if __name__ == "__main__":
    main()
