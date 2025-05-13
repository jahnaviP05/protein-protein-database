import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
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
        df.columns = df.columns.str.strip()
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

    col1, col2, col3 = st.columns(3)
    box_style = "background-color:#f5f5f5; padding:20px; border-radius:10px; min-height:180px; text-align:center;"

    with col1:
        st.markdown(f"<div style='{box_style}'><h3>🔬 Why This Database?</h3><p>This database helps researchers explore disease-specific <b>protein-protein interactions</b>, understand molecular mechanisms, and aid <b>drug discovery</b>.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='{box_style}'><h3>🌐 About Visualization</h3><p>Our interactive network graph highlights <b>protein interactions</b> based on scores.</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='{box_style}'><h3>🔍 How to Search?</h3><p>Use the search box to find interactions for a <b>single</b> or <b>multiple</b> proteins.</p></div>", unsafe_allow_html=True)

    st.markdown("✏ **Edit the Data**")
    st.markdown("🔗 [*Edit or Add Data on GitHub*](https://github.com/jahnaviP05/protein-protein-database/edit/main/cleaned_interactions.csv)")

# ✅ Data Page
elif page == "Data":
    st.subheader("Protein-Protein Interaction Data")

    single_protein = st.text_input("🔍 Search for a Single Protein:", "").strip()
    multi_proteins = st.text_area("🔍 Search for Multiple Proteins (comma-separated):", "").strip()

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
        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(label="📥 Download Data as CSV", data=csv_data, file_name="filtered_ppi_data.csv", mime="text/csv")

# ✅ Visualization Page
elif page == "Visualization":
    st.subheader("Protein-Protein Interaction Network")

    search_protein = st.text_input("🔍 Search for a Single Protein:", "").strip()
    multi_proteins_input = st.text_area("🔍 Search for Multiple Proteins (comma-separated):", "").strip()

    filtered_df = df
    if search_protein:
        filtered_df = df[(df["Protein_A"] == search_protein) | (df["Protein_B"] == search_protein)]
    if multi_proteins_input:
        protein_list = [p.strip() for p in multi_proteins_input.split(",")]
        filtered_df = df[df["Protein_A"].isin(protein_list) | df["Protein_B"].isin(protein_list)]

    if filtered_df.empty:
        st.warning("⚠ No interactions found.")
    else:
        # ✅ Bar Chart
        st.subheader("📊 Interaction Score Distribution")
        filtered_df["interaction"] = filtered_df["Protein_A"] + " ↔ " + filtered_df["Protein_B"]
        scores = filtered_df["combined_score"]
        labels = filtered_df["interaction"]

        colors = [
            "#ff69b4" if s >= 0.9 else "#3498db" if s >= 0.7 else "#9b59b6"
            for s in scores
        ]

        fig, ax = plt.subplots(figsize=(15, 6))
        bars = ax.bar(labels, scores, color=colors)
        ax.set_ylabel("Combined Score")
        ax.set_xlabel("Protein Interactions")
        ax.set_title("Interaction Scores by Protein Pair")
        plt.xticks(rotation=90)
        plt.tight_layout()
        st.pyplot(fig)

        # ✅ Network Graph
        G = nx.Graph()
        for _, row in filtered_df.iterrows():
            a, b = row["Protein_A"], row["Protein_B"]
            score = row.get("combined_score", 1)
            distance = 1.0 / score if score > 0 else 1.0
            G.add_edge(a, b, weight=distance, label=f"{score:.2f}")

        pos = nx.spring_layout(G, weight='weight', seed=42)
        network_buffer = io.BytesIO()

        plt.figure(figsize=(14, 10))
        nx.draw_networkx_nodes(G, pos, node_size=600, node_color="#1f78b4")
        nx.draw_networkx_edges(G, pos, edge_color="#999999", width=2)
        nx.draw_networkx_labels(G, pos, font_color="black", font_size=10)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

        plt.savefig(network_buffer, format="png")
        network_buffer.seek(0)
        st.image(network_buffer)

        # ✅ UniProt Integration
        st.subheader("🔗 UniProt Search & External Links")

        all_proteins = set(filtered_df["Protein_A"]).union(filtered_df["Protein_B"])
        selected_protein = st.selectbox("🔍 Select a Protein to View on UniProt:", sorted(all_proteins))

        if selected_protein:
            uniprot_url = f"https://www.uniprot.org/uniprotkb/?query={selected_protein}&sort=score"
            st.markdown(f"🔗 [Click here to view **{selected_protein}** on UniProt]({uniprot_url})", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("💡 *Note: This opens the UniProt search page for the selected protein.*")
