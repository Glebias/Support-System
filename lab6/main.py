LATIN_ALPHABET = [chr(i) for i in range(ord('A'), ord('Z') + 1)]

class HashTable:
    def __init__(self, table_size=128):
        self.table_size = table_size
        self.table = [None] * self.table_size

    def _char_to_index(self, char):
        char = char.upper()
        if char not in LATIN_ALPHABET:
            raise ValueError(f"Invalid character: {char}. Only A–Z are allowed.")
        return LATIN_ALPHABET.index(char)

    def _hash(self, key):
        key = key.upper()
        if len(key) < 2:
            raise ValueError("Key must be at least 2 characters long")
        idx1 = self._char_to_index(key[0])
        idx2 = self._char_to_index(key[1])
        return (idx1 * 26 + idx2) % self.table_size

    def insert(self, key, value):
        idx = self._hash(key)
        start_idx = idx
        while self.table[idx] is not None:
            if self.table[idx][0] == key:
                self.table[idx] = (key, value)
                return
            idx = (idx + 1) % self.table_size
            if idx == start_idx:
                raise Exception("Hash table is full")
        self.table[idx] = (key, value)

    def get(self, key):
        idx = self._hash(key)
        start_idx = idx
        while self.table[idx] is not None:
            if self.table[idx][0] == key:
                return self.table[idx][1]
            idx = (idx + 1) % self.table_size
            if idx == start_idx:
                break
        return None

    def update(self, key, new_value):
        idx = self._hash(key)
        start_idx = idx
        while self.table[idx] is not None:
            if self.table[idx][0] == key:
                self.table[idx] = (key, new_value)
                return
            idx = (idx + 1) % self.table_size
            if idx == start_idx:
                break
        raise KeyError("Key not found")

    def delete(self, key):
        idx = self._hash(key)
        start_idx = idx
        while self.table[idx] is not None:
            if self.table[idx][0] == key:
                self.table[idx] = None
                return
            idx = (idx + 1) % self.table_size
            if idx == start_idx:
                break
        raise KeyError("Key not found")

    def display(self):
        for i, item in enumerate(self.table):
            if item is not None:
                print(f"[{i}] {item[0]} → {item[1]}")

# ======= CLI Interface =======
def main():
    ht = HashTable()

    while True:
        print("\n--- Hash Table Menu ---")
        print("1. Insert")
        print("2. Search")
        print("3. Update")
        print("4. Delete")
        print("5. Display")
        print("0. Exit")
        choice = input("Select an option: ")

        try:
            if choice == '1':
                key = input("Enter key (at least 2 Latin letters): ")
                value = input("Enter value: ")
                ht.insert(key, value)
                print("Inserted successfully.")
            elif choice == '2':
                key = input("Enter key: ")
                result = ht.get(key)
                print(f"Value: {result}" if result else "Key not found.")
            elif choice == '3':
                key = input("Enter key to update: ")
                value = input("Enter new value: ")
                ht.update(key, value)
                print("Updated successfully.")
            elif choice == '4':
                key = input("Enter key to delete: ")
                ht.delete(key)
                print("Deleted successfully.")
            elif choice == '5':
                ht.display()
            elif choice == '0':
                print("Goodbye!")
                break
            else:
                print("Invalid option.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
