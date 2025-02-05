import { Tab } from "@headlessui/react";
import { TabItem } from "../../utils/constants";

export interface TabsProps<T> {
    tabItems: TabItem<T>[];
    data?: T;
    tabListClassName?: string;
    tabPanelsClassName?: string;
}

const Tabs = <T,>({
    tabItems,
    data,
    tabListClassName = "",
    tabPanelsClassName = "",
}: TabsProps<T>) => {
    return (
        <Tab.Group>
            <Tab.List
                className={`p-5 flex md:flex-row items-center border-b flex-col md:justify-between ${tabListClassName}`}
            >
                {tabItems.map(({ id, label }) => (
                    <Tab key={id} className="focus:outline-none">
                        {label}
                    </Tab>
                ))}
            </Tab.List>
            <Tab.Panels className={`p-5 ${tabPanelsClassName}`}>
                {tabItems.map(({ id, renderTabPanelComponent }) => (
                    <Tab.Panel key={id}>
                        {data ? (
                            renderTabPanelComponent(data)
                        ) : (
                            <p>Not found</p>
                        )}
                    </Tab.Panel>
                ))}
            </Tab.Panels>
        </Tab.Group>
    );
};

export default Tabs;
