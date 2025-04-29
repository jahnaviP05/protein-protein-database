
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random
import io

# ✅ Page Config
st.set_page_config(page_title="Protein-Protein Interaction Database for Human Diseases", layout="wide")

# ✅ GitHub CSV URL
GITHUB_CSV_URL = "https://raw.githubusercontent.com/jahnaviP05/protein-protein-database/main/cleaned_interactions.csv"

# ✅ Load Data Function
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(GITHUB_CSV_URL, encoding="utf-8")
        df.columns = df.columns.str.strip()  # Clean column names
        return df
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# ✅ Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Data", "Visualization"])

# ✅ Home Page
if page == "Home":
    st.markdown("<h1 style='text-align: center;'>Protein-Protein Interaction Database for Human Diseases</h1>", unsafe_allow_html=True)

    # ✅ Three Equal-Sized Boxes
    col1, col2, col3 = st.columns(3)

    box_style = "background-color:#f5f5f5; padding:20px; border-radius:10px; min-height:180px; text-align:center;"

    with col1:
        st.markdown(
            f"<div style='{box_style}'>"
            "<h3>🔬 Why This Database?</h3>"
            "<p>This database helps researchers explore disease-specific <b>protein-protein interactions</b>, understand molecular mechanisms, and aid <b>drug discovery</b>.</p>"
            "</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"<div style='{box_style}'>"
            "<h3>🌐 About Visualization</h3>"
            "<p>Our interactive network graph highlights <b>protein interactions</b> with color-coded edges for interaction strength.</p>"
            "</div>", unsafe_allow_html=True)

    with col3:
        st.markdown(
            f"<div style='{box_style}'>"
            "<h3>🔍 How to Search?</h3>"
            "<p>Use the search box to find interactions for a <b>single</b> or <b>multiple</b> proteins and visualize their network.</p>"
            "</div>", unsafe_allow_html=True)

    # ✅ GitHub Edit Link
    st.markdown("✏ **Edit the Data**")
    st.markdown("🔗 [*Edit or Add Data on GitHub*](https://github.com/jahnaviP05/protein-protein-database/edit/main/cleaned_interactions.csv)")

# ✅ Data Page
elif page == "Data":
    st.subheader("Protein-Protein Interaction Data")

    # ✅ Single Protein Search
    single_protein = st.text_input("🔍 Search for a Single Protein:", "").strip()

    # ✅ Multi-Protein Search Box
    multi_proteins = st.text_area("🔍 Search for Multiple Proteins (comma-separated):", "").strip()

    # ✅ Filter Data
    df_filtered = df
    if single_protein:
        df_filtered = df[(df["Protein_A"] == single_protein) | (df["Protein_B"] == single_protein)]
    
    if multi_proteins:
        protein_list = [p.strip() for p in multi_proteins.split(",")]
        df_filtered = df[df["Protein_A"].isin(protein_list) | df["Protein_B"].isin(protein_list)]

    if df_filtered.empty:
        st.warning("⚠ No interactions found.")
    else:
        st.dataframe(df_filtered)

        # ✅ Download Data as CSV
        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(label="📥 Download Data as CSV", data=csv_data, file_name="filtered_ppi_data.csv", mime="text/csv")

# ✅ Visualization Page
elif page == "Visualization":
    st.subheader("Protein-Protein Interaction Network")

    # ✅ Single Protein Search
    search_protein = st.text_input("🔍 Search for a Single Protein:", "").strip()

    # ✅ Multi-Protein Search Box
    multi_proteins_input = st.text_area("🔍 Search for Multiple Proteins (comma-separated):", "").strip()

    # ✅ Filter Data
    filtered_df = df
    if search_protein:
        filtered_df = df[(df["Protein_A"] == search_protein) | (df["Protein_B"] == search_protein)]
    
    if multi_proteins_input:
        protein_list = [p.strip() for p in multi_proteins_input.split(",")]
        filtered_df = df[df["Protein_A"].isin(protein_list) | df["Protein_B"].isin(protein_list)]

    if filtered_df.empty:
        st.warning("⚠ No interactions found.")
    else:
        # ✅ Create Graph
        G = nx.Graph()
        for _, row in filtered_df.iterrows():
            G.add_edge(row["Protein_A"], row["Protein_B"], weight=row.get("combined_score", 1))

        # ✅ Generate Light Colors for Nodes
        color_palette = [
            "#AED6F1", "#D4EFDF", "#FAD7A0", "#F5B7B1", 
            "#D7BDE2", "#A3E4D7", "#F9E79F", "#E8DAEF", 
            "#D5F5E3", "#FCF3CF", "#FADBD8", "#EBDEF0"
        ]
        node_colors = random.choices(color_palette, k=len(G.nodes()))

        # ✅ Assign Same Size to All Nodes
        node_sizes = 600  

        # ✅ Assign Different Edge Colors Based on Interaction Strength
        edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
        edge_colors = [plt.cm.cool(w / max(edge_weights, default=1)) for w in edge_weights]

        # ✅ Graph Layout & Styling
        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(G, seed=42)

        nx.draw(
            G, pos, with_labels=True, node_size=node_sizes, node_color=node_colors,
            edge_color=edge_colors, edge_cmap=plt.cm.cool,
            font_size=10, font_color="black", alpha=0.9
        )

        # ✅ Save Graph to Bytes and Provide Download Option
        graph_buffer = io.BytesIO()
        plt.savefig(graph_buffer, format="png")
        graph_buffer.seek(0)

        st.pyplot(plt)

        # ✅ Download Graph Option
        st.download_button(label="📥 Download Network Graph", data=graph_buffer, file_name="ppi_network.png", mime="image/png")

        # ✅ Show Interaction Details Below Graph
        st.subheader("📄 Interaction Details")
        st.dataframe(filtered_df)

        # ✅ **UniProt Integration**
        st.subheader("🧬 Protein Details")
        for protein in set(filtered_df["Protein_A"]).union(set(filtered_df["Protein_B"])):
            uniprot_link = f"https://www.uniprot.org/uniprot/?query={protein}&sort=score"
            st.markdown(f"🔗 **UniProt:** [{protein}]({uniprot_link})")

