"""
Example: Populating vEPC Documentation into Vector Database

This script shows how to add vEPC documentation to the ChromaDB vector database
for knowledge retrieval.
"""

import chromadb
from chromadb.config import Settings
from config.vepc_settings import VEPC_VECTORDB_PATH, VEPC_VECTORDB_COLLECTION


def populate_vepc_docs():
    """Populate vEPC documentation into ChromaDB."""

    # Initialize ChromaDB client
    client = chromadb.Client(
        Settings(
            persist_directory=VEPC_VECTORDB_PATH,
            anonymized_telemetry=False,
        )
    )

    # Get or create collection
    collection = client.get_or_create_collection(
        name=VEPC_VECTORDB_COLLECTION
    )

    # Example vEPC documentation
    documents = [
        # Timers
        {
            "content": "T3412 is the periodic Tracking Area Update (TAU) timer. It controls how often a UE performs periodic TAU to inform the network of its presence. Typical values range from 54 minutes to 310 hours. Setting it too low increases signaling load; too high may delay paging.",
            "metadata": {"category": "timers", "parameter": "t3412", "type": "configuration"}
        },
        {
            "content": "T3402 is the attach retry timer. When an attach request is rejected, the UE waits for this timer before retrying. Default is 12 minutes. Used to prevent excessive attach attempts that could overload the MME.",
            "metadata": {"category": "timers", "parameter": "t3402", "type": "configuration"}
        },
        {
            "content": "T3410 is the paging timer. The MME waits for this duration for a paging response from the UE. If no response is received, the MME may retry paging or consider the UE unreachable. Typical value is 2-4 seconds.",
            "metadata": {"category": "timers", "parameter": "t3410", "type": "configuration"}
        },

        # Network Identity
        {
            "content": "MCC (Mobile Country Code) is a 3-digit code that identifies the country. For example, 310 is USA, 460 is China, 452 is Vietnam. It's part of the PLMN identity along with MNC.",
            "metadata": {"category": "network_identity", "parameter": "mcc", "type": "configuration"}
        },
        {
            "content": "MNC (Mobile Network Code) is a 2 or 3-digit code that identifies the mobile network operator within a country. Combined with MCC, it forms the PLMN ID. For example, MCC=310 + MNC=410 identifies AT&T in the USA.",
            "metadata": {"category": "network_identity", "parameter": "mnc", "type": "configuration"}
        },
        {
            "content": "MME Code is used to uniquely identify an MME within an MME pool. It's part of the GUMMEI (Globally Unique MME Identifier). Valid range is 0-255. Used for load balancing and MME selection.",
            "metadata": {"category": "network_identity", "parameter": "mme_code", "type": "configuration"}
        },

        # Features
        {
            "content": "CSFB (Circuit Switched Fallback) allows LTE devices to fall back to 2G/3G networks for voice calls when VoLTE is not available. The UE temporarily leaves LTE, completes the call on the legacy network, then returns to LTE.",
            "metadata": {"category": "features", "parameter": "csfb", "type": "concept"}
        },
        {
            "content": "SRVCC (Single Radio Voice Call Continuity) enables seamless handover of VoLTE calls to 2G/3G networks when LTE coverage is lost. Unlike CSFB, the call continues without interruption during the handover.",
            "metadata": {"category": "features", "parameter": "srvcc", "type": "concept"}
        },
        {
            "content": "VoLTE (Voice over LTE) enables voice calls over the LTE network using IMS. It provides better voice quality, faster call setup, and allows simultaneous voice and data. Requires IMS core and specific bearer configurations.",
            "metadata": {"category": "features", "parameter": "volte", "type": "concept"}
        },

        # Troubleshooting
        {
            "content": "Attach failure troubleshooting: 1) Check MME logs for reject cause. 2) Verify PLMN configuration (MCC/MNC). 3) Check HSS connectivity and subscriber profile. 4) Verify S1 interface status. 5) Check for capacity limits (max UE). Common causes: authentication failure, unknown PLMN, MME overload.",
            "metadata": {"category": "troubleshooting", "issue": "attach_failure", "type": "guide"}
        },
        {
            "content": "High S1 latency troubleshooting: 1) Check network path between eNodeB and MME. 2) Verify SCTP association health. 3) Check MME CPU and memory usage. 4) Review S1AP message processing times. 5) Check for packet loss or retransmissions. May indicate network congestion or MME overload.",
            "metadata": {"category": "troubleshooting", "issue": "s1_latency", "type": "guide"}
        },
        {
            "content": "UE registration failure: 1) Verify TAI list configuration. 2) Check if UE's IMSI is provisioned in HSS. 3) Review authentication vectors. 4) Check for MME capacity limits. 5) Verify security algorithms match between UE and network. Common reject causes: IMSI unknown in HSS, network failure, congestion.",
            "metadata": {"category": "troubleshooting", "issue": "registration_failure", "type": "guide"}
        },
    ]

    # Add documents to collection
    for i, doc in enumerate(documents):
        collection.add(
            documents=[doc["content"]],
            metadatas=[doc["metadata"]],
            ids=[f"vepc_doc_{i}"]
        )

    print(f"Successfully added {len(documents)} documents to {VEPC_VECTORDB_COLLECTION}")
    print(f"Vector database location: {VEPC_VECTORDB_PATH}")


if __name__ == "__main__":
    populate_vepc_docs()
