import streamlit
from ssr_conversion import generate_output, generate_output_from_binary
import streamlit.components.v1 as stc
from fnxns import *
from sqlite3_fxns import *
import pandas as pd
import sqlite3


HTML_BANNER = """
    <div style="background-color:#464e5f;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">SSR Conversion</h1>
    </div>
    """


def main():
    """SSR Conversion"""
    stc.html(HTML_BANNER)

    alldata_list = view_all_data()

    if not alldata_list:
        species_list = []
        all_alleles = []
    else:
        species_list = list(set([x[1] for x in alldata_list]))
        all_alleles = list(set([x[0] for x in alldata_list]))

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
            '<h align="center"><font size="8"><mark style="background-color: lightgrey">*SSR '
            "Conversion*</mark> is a streamlit application for converting SRR genotyping "
            "data into a binary format, for presence/absence of the marker allele, or vice versa.</font></h>",
            unsafe_allow_html=True,
        )

    elif choice == "Help":
        st.markdown(
            '<font size="6">\n\n- Input data is a '
            "<b>comma-separated (CSV)</b> file that can contain 2 types of data, depending on the format conversion "
            "requested by the user:</font>\n\n", unsafe_allow_html=True)

        st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Input file for <b>numeric-to-binary</b> "
                    "conversion:", unsafe_allow_html=True)
        st.code(
            "Line,cesi98,cesi976,cesi17,...\n"
            "1124/20,185,273,193,...\n"
            "1125/20,185/191,273,193,...\n"
            "1131/20,-,273,-,...\n\n"
        )

        st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- Input file for <b>binary-to-numeric</b> "
                    "conversion:", unsafe_allow_html=True)
        st.code(
            "Line,cesi98_185,cesi98_191,cesi976_273,cesi17_193,...\n"
            "1124/20,1,0,1,1,...\n"
            "1125/20,1,1,1,1,...\n"
            "1131/20,-,-,1,-,...\n\n"
        )

        st.markdown(
            '<font size="8">\n\nTracks</font>\n\n',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<font size="6">\n\n- "Species info" Track</font>\n\n',
            unsafe_allow_html=True,
        )
        st.markdown(
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;In this track you can see a table with all the "
            "marker alleles (marker name + '_' + allele size), grouped by species.",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<font size="6">\n\n- "Add new species and/or markers" Track</font>\n\n',
            unsafe_allow_html=True,
        )
        st.text("Marker file example:")
        st.code(
            "cesi98_182\n"
            "cesi98_185\n"
            "cesi98_191\n"
            "cesi976_271\n"
            "cesi976_273\n"
            "cesi17_190\n"
            "cesi17_193\n"
        )
        st.markdown(
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;User can either add a new species, "
            "followed by a set of marker alleles, or add a new marker allele into an existing species database.",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<font size="6">\n\n- "Format conversion" Track</font>\n\n',
            unsafe_allow_html=True,
        )
        st.markdown(
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Conversion of per-line SSR alleles into allele-based"
            " binary format (<i>numeric-to-binary</i> option) or allele-based binary format into per-line SSR alleles "
            "(<i>binary-to-numeric</i> option).",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<font size="8">\n\nData testing</font>\n\n',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<font size="6">\n\n- markers_for_species.csv: input file for adding markers into the database.</font>\n\n',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<font size="46">\n\n- numeric_input.csv: input file for passing SSR allele format into a binary '
            'format.</font>\n\n',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<font size="6">\n\n- binary_input.csv: input file for passing binary data into an SSR allele '
            'format.</font>\n\n',
            unsafe_allow_html=True,
        )

    elif choice == "Species info":

        if alldata_list:
            df = pd.DataFrame(alldata_list)
            df.columns = ["Marker_name", "Species", "User", "Date_added"]

            st.write(
                "Species available in the database, with their corresponding SSR markers:"
            )
            st.dataframe(df, hide_index=True)

            st.markdown("#### Download Database ###")
            FileDownloader(
                df.to_csv(index=False),
                filename="markers_in_database",
            ).download()
        else:
            st.warning(
                'No species table available. Please run "Add species and/or markers" from sidebar menu to add a new '
                "species and/or markers for a species."
            )
            exit(0)

    elif choice == "Add species and/or markers":

        timestr = time.strftime("%Y-%m-%d")
        conn = sqlite3.connect('species.sqlite')
        cur = conn.cursor()

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

            new_alleles_file = st.file_uploader("Upload marker file", type=["txt", "csv"])

            if new_alleles_file is not None and new_species is not None:

                cur.execute('''CREATE TABLE IF NOT EXISTS data (markerid TEXT, species TEXT,
                person TEXT, uploadDate TIMESTAMP, UNIQUE(markerid))''')

                alleles_list = pd.read_csv(new_alleles_file, header=None).values.tolist()

                markerlist = []
                for i in alleles_list:
                    markerlist.append([i[0], new_species, user, timestr])

                skipped_markers = list()
                for m in markerlist:
                    try:
                        query = f"INSERT INTO data (markerid, species, person, uploadDate) VALUES (?, ?, ?, ?)"
                        cur.execute(query, tuple(m))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        skipped_markers.append(m[0])

                st.success(
                    "%s markers were added to the database correctly" % new_species.upper()
                )
                if len(skipped_markers) > 0:
                    streamlit.warning('%d markers are already present in the DB and were not added.' % len(skipped_markers))
        else:
            if not species_list:
                st.warning(
                    'You do not have any species and/or markers added. Please add a species and a set of markers by selecting "yes" from above.')
            else:
                st.markdown(
                    "##### It looks like that you want to add a new set of markers to an existing species. #####"
                )
                st.markdown(
                    "###### Please fill in the information below: ######"
                )

                user = st.text_input("Introduce your full name")
                selected_species = st.selectbox("Select species from list:", species_list)
                new_markers = st.text_area("Provide new marker(s); one per line")
                marker_addition = st.button("Add markers")

                if marker_addition:
                    (
                        common_markers,
                        new_marker_list

                    ) = detect_duplicate_markers(new_markers, selected_species)
                    if len(common_markers) != 0:
                        st.write(
                            "Marker(s) %s already present in the %s database. Ignoring..."
                            % (common_markers, selected_species)
                        )
                        for x in common_markers:
                            new_marker_list.remove(x)

                        if not new_marker_list:
                            st.warning('All the provided markers are already present in the database, for the species '
                                       'selected.\n\n##### No marker is added to the database #####')
                        else:
                            add_markers(selected_species, new_marker_list, user, timestr, cur)
                            st.success(
                                "Marker(s) %s were added successfully to the %s database"
                                % (new_marker_list, selected_species.upper())
                            )
                    else:
                        add_markers(selected_species, new_marker_list, user, timestr, conn)
                        st.success(
                            "Marker(s) %s were added successfully to the %s database"
                            % (new_marker_list, selected_species.upper())
                        )

                    new_data = view_species_data(selected_species)
                    new_data2 = sorted([x for x in new_data], key=lambda x: x[0].lower())
                    df = pd.DataFrame(new_data2, columns=["%s markers" % selected_species])
                    st.markdown(
                        "###### Below you the have the current list of markers for %s: ######"
                        % selected_species.upper()
                    )
                    st.table(df)

    elif choice == "Format conversion":

        st.subheader("Data Conversion")
        selected_species = st.selectbox("Select species of interest", species_list)

        if not selected_species:
            st.error("Remember to add a species to the database before proceeding!!!!")
        else:
            in_data = st.file_uploader("Upload you data", type=["csv"])
            st.warning(
                "Please make sure that non-utf8 characters are not present in marker IDs "
                "(e.g. í, ó, é, á, ñ, etc.)"
            )

            if in_data is not None:
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

                tochoose = ['numeric-to-binary', 'binary-to-numeric']

                conversion_type = st.radio('Convert to', tochoose, horizontal=True, index=0)

                ordered_alleles = sorted(all_alleles, key=lambda x: x.lower())

                if conversion_type == 'numeric-to-binary':
                    st.write('Convert marker alleles per line information into allele presence/absence information')
                    convert = st.button("##### Run data conversion #####")
                    if convert:
                        results_df = generate_output(dataf, ordered_alleles)

                        st.success("Data conversion completed successfully!")
                        with st.expander("##### Converted Data #####"):
                            st.dataframe(results_df)

                        st.markdown("#### Download File ###")
                        FileDownloader(
                            results_df.to_csv(index=False),
                            filename=in_data.name.split(".")[0] + "-binary",
                        ).download()

                if conversion_type == 'binary-to-numeric':
                    st.write('Convert allele presence/absence information into marker alleles per line')
                    convert = st.button("##### Run data conversion #####")
                    if convert:
                        results_df = generate_output_from_binary(dframe=dataf, alleles_list=ordered_alleles)

                        st.success("Data conversion completed successfully!")
                        with st.expander("##### Converted Data #####"):
                            st.dataframe(results_df)

                        st.markdown("#### Download File ###")
                        FileDownloader(
                            results_df.to_csv(index=False),
                            filename=in_data.name.split(".")[0] + "-numeric",
                        ).download()


if __name__ == "__main__":
    main()
