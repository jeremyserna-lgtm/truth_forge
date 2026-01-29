Based on the sources, the local training of the **Llama 4 Scout (109B)** model is enabled by a specific hardware cluster configuration known as **"The Empire."**  
This configuration aggregates the Unified Memory of four Mac Studio machines to create a single memory pool sufficient for **full fine-tuning** (not just LoRA) of the 109B parameter model.

### 1\. "The Empire" Cluster Specifications

The training infrastructure consists of **four Mac Studios** connected via high-speed interconnects (Thunderbolt 5/10Gb Ethernet) using **MLX** and **MPI** for distributed training. The total pooled memory is **1.28TB** 1, 2, 3\.

* **The King (Coordinator \+ Compute):**  
* **Chip:** Apple M3 Ultra  
* **Cores:** 32-core CPU, 80-core GPU, 32-core Neural Engine  
* **Memory:** **512GB** Unified Memory 4, 1\.  
* **The Soldiers (x3 Compute Nodes):**  
* **Chip:** Apple M3 Ultra  
* **Cores:** 28-core CPU, 60-core GPU, 32-core Neural Engine  
* **Memory:** **256GB** Unified Memory *each* 5, 1\.

### 2\. Memory Requirements vs. Capacity

To perform a **full fine-tune** on the 109B Scout model (updating all weights rather than using adapters), the system utilizes "Zero-Degradation Optimizations."

* **Required Memory (Optimized):** Approximately **\~700GB** 6, 7, 3\.  
* **Available Capacity:** **1,280GB** (1.28TB) 6\.  
* **Headroom:** Approximately **\~580GB** of free memory, ensuring stable operation 8, 9\.

### 3\. Optimization Stack

The local training relies on specific software optimizations to fit the model within the 1.28TB pool without degrading model quality. These include:

* **Mixed Precision (bf16)**  
* **Gradient Checkpointing**  
* **ZeRO Stage 2**  
* **8-bit Optimizers** 6, 7\.

This setup allows the "Truth Engine" to maintain **sovereign control** over the training process for the Genesis model, ensuring no data leaves the local environment for the primary training phase 8\. While inference for the 109B model (quantized to 4-bit) can run on a single machine with \~55-60GB of memory, the heavy lifting of full training requires this specific cluster 10\.  
